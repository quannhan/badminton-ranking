"""
Script to remove all 2-point (water bet) matches from the database
and recalculate user points accordingly.

⚠️  WARNING: This will permanently delete all stake_value = 2 matches!
Make sure to backup your database before running this script.

Usage:
    python remove_water_bets_script.py
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Load environment variables
load_dotenv()

# Get database URL
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    print("❌ ERROR: DATABASE_URL not found in environment variables")
    sys.exit(1)

# Create engine
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def get_water_bet_stats(session):
    """Get statistics about water bets before deletion"""
    query = text("""
        SELECT 
            COUNT(*) as total_water_matches,
            SUM(CASE WHEN status = 'APPROVED' THEN 1 ELSE 0 END) as approved,
            SUM(CASE WHEN status = 'PENDING' THEN 1 ELSE 0 END) as pending,
            SUM(CASE WHEN status = 'REJECTED' THEN 1 ELSE 0 END) as rejected
        FROM match_reports 
        WHERE stake_value = 2
    """)
    result = session.execute(query).fetchone()
    return result

def get_affected_users(session):
    """Get users who will be affected by the deletion"""
    query = text("""
        SELECT 
            u.user_id,
            u.display_name,
            u.total_points as current_total,
            u.singles_points as current_singles,
            u.doubles_points as current_doubles,
            COALESCE(SUM(mp.points_earned), 0) as points_to_deduct,
            COALESCE(SUM(CASE WHEN mr.match_type = 'SINGLES' THEN mp.points_earned ELSE 0 END), 0) as singles_to_deduct,
            COALESCE(SUM(CASE WHEN mr.match_type != 'SINGLES' THEN mp.points_earned ELSE 0 END), 0) as doubles_to_deduct
        FROM users u
        JOIN match_players mp ON u.user_id = mp.user_id
        JOIN match_reports mr ON mp.match_id = mr.match_id
        WHERE mr.stake_value = 2 AND mr.status = 'APPROVED'
        GROUP BY u.user_id, u.display_name, u.total_points, u.singles_points, u.doubles_points
        ORDER BY points_to_deduct DESC
    """)
    return session.execute(query).fetchall()

def remove_water_bets(session):
    """Execute the removal of water bets and update user points"""
    
    # Step 1: Update user points
    print("\n📊 Updating user points...")
    update_query = text("""
        UPDATE users u
        SET 
            total_points = u.total_points - COALESCE((
                SELECT SUM(mp.points_earned)
                FROM match_players mp
                JOIN match_reports mr ON mp.match_id = mr.match_id
                WHERE mp.user_id = u.user_id AND mr.stake_value = 2 AND mr.status = 'APPROVED'
            ), 0),
            singles_points = u.singles_points - COALESCE((
                SELECT SUM(mp.points_earned)
                FROM match_players mp
                JOIN match_reports mr ON mp.match_id = mr.match_id
                WHERE mp.user_id = u.user_id AND mr.stake_value = 2 AND mr.status = 'APPROVED' AND mr.match_type = 'SINGLES'
            ), 0),
            doubles_points = u.doubles_points - COALESCE((
                SELECT SUM(mp.points_earned)
                FROM match_players mp
                JOIN match_reports mr ON mp.match_id = mr.match_id
                WHERE mp.user_id = u.user_id AND mr.stake_value = 2 AND mr.status = 'APPROVED' AND mr.match_type != 'SINGLES'
            ), 0),
            updated_at = NOW()
        WHERE u.user_id IN (
            SELECT DISTINCT mp.user_id
            FROM match_players mp
            JOIN match_reports mr ON mp.match_id = mr.match_id
            WHERE mr.stake_value = 2 AND mr.status = 'APPROVED'
        )
    """)
    result = session.execute(update_query)
    print(f"✅ Updated {result.rowcount} users")
    
    # Step 2: Delete match_players
    print("\n🗑️  Deleting match players...")
    delete_players_query = text("""
        DELETE FROM match_players 
        WHERE match_id IN (
            SELECT match_id FROM match_reports WHERE stake_value = 2
        )
    """)
    result = session.execute(delete_players_query)
    print(f"✅ Deleted {result.rowcount} match player records")
    
    # Step 3: Delete match_reports
    print("\n🗑️  Deleting match reports...")
    delete_matches_query = text("""
        DELETE FROM match_reports WHERE stake_value = 2
    """)
    result = session.execute(delete_matches_query)
    print(f"✅ Deleted {result.rowcount} match reports")
    
    # Step 4: Verify no negative points
    verify_query = text("""
        SELECT user_id, display_name, total_points, singles_points, doubles_points
        FROM users
        WHERE total_points < 0 OR singles_points < 0 OR doubles_points < 0
    """)
    negative_users = session.execute(verify_query).fetchall()
    
    if negative_users:
        print("\n⚠️  WARNING: Found users with negative points!")
        for user in negative_users:
            print(f"   User {user.display_name}: Total={user.total_points}, Singles={user.singles_points}, Doubles={user.doubles_points}")
        return False
    
    return True

def main():
    print("=" * 70)
    print("🗑️  REMOVE WATER BETS (2-POINT MATCHES) SCRIPT")
    print("=" * 70)
    
    session = Session()
    
    try:
        # Show statistics
        print("\n📊 Getting water bet statistics...")
        stats = get_water_bet_stats(session)
        
        if stats.total_water_matches == 0:
            print("✅ No water bets found in the database!")
            return
        
        print(f"\n📈 Water Bet Statistics:")
        print(f"   Total matches: {stats.total_water_matches}")
        print(f"   - Approved: {stats.approved}")
        print(f"   - Pending: {stats.pending}")
        print(f"   - Rejected: {stats.rejected}")
        
        # Show affected users
        print("\n👥 Affected users:")
        affected_users = get_affected_users(session)
        
        if not affected_users:
            print("   No users with points from water bets")
        else:
            print(f"\n   {'User':<20} {'Current':<10} {'To Deduct':<12} {'New Total':<10}")
            print("   " + "-" * 55)
            for user in affected_users:
                new_total = user.current_total - user.points_to_deduct
                print(f"   {user.display_name:<20} {user.current_total:<10} {user.points_to_deduct:<12} {new_total:<10}")
        
        # Confirmation
        print("\n" + "=" * 70)
        print("⚠️  WARNING: This action cannot be undone!")
        print("=" * 70)
        response = input("\n❓ Do you want to proceed? Type 'YES' to confirm: ")
        
        if response != "YES":
            print("\n❌ Operation cancelled")
            return
        
        # Execute removal
        print("\n🚀 Starting removal process...")
        success = remove_water_bets(session)
        
        if success:
            # Commit transaction
            session.commit()
            print("\n" + "=" * 70)
            print("✅ SUCCESSFULLY REMOVED ALL WATER BETS!")
            print("=" * 70)
            
            # Final verification
            final_stats = get_water_bet_stats(session)
            print(f"\n✅ Remaining water bets: {final_stats.total_water_matches}")
        else:
            session.rollback()
            print("\n❌ Operation rolled back due to negative points")
            
    except Exception as e:
        session.rollback()
        print(f"\n❌ ERROR: {str(e)}")
        print("Transaction rolled back")
        
    finally:
        session.close()

if __name__ == "__main__":
    main()
