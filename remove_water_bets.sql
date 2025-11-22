-- =====================================================
-- Script to remove all 2-point matches (water bets)
-- and recalculate user points
-- =====================================================

BEGIN;

-- Step 1: Get all match_ids with stake_value = 2
CREATE TEMP TABLE water_bet_matches AS
SELECT match_id FROM match_reports WHERE stake_value = 2;

-- Step 2: Get all affected user_ids and their points earned from water bets
CREATE TEMP TABLE water_bet_points AS
SELECT 
    mp.user_id,
    SUM(mp.points_earned) as total_water_points,
    mr.match_type
FROM match_players mp
JOIN match_reports mr ON mp.match_id = mr.match_id
WHERE mr.stake_value = 2 AND mr.status = 'APPROVED'
GROUP BY mp.user_id, mr.match_type;

-- Step 3: Show affected users before deletion (for verification)
SELECT 
    u.user_id,
    u.display_name,
    u.total_points as current_total,
    u.singles_points as current_singles,
    u.doubles_points as current_doubles,
    COALESCE(SUM(CASE WHEN wbp.match_type = 'SINGLES' THEN wbp.total_water_points ELSE 0 END), 0) as singles_to_deduct,
    COALESCE(SUM(CASE WHEN wbp.match_type != 'SINGLES' THEN wbp.total_water_points ELSE 0 END), 0) as doubles_to_deduct,
    u.total_points - COALESCE(SUM(wbp.total_water_points), 0) as new_total,
    u.singles_points - COALESCE(SUM(CASE WHEN wbp.match_type = 'SINGLES' THEN wbp.total_water_points ELSE 0 END), 0) as new_singles,
    u.doubles_points - COALESCE(SUM(CASE WHEN wbp.match_type != 'SINGLES' THEN wbp.total_water_points ELSE 0 END), 0) as new_doubles
FROM users u
LEFT JOIN water_bet_points wbp ON u.user_id = wbp.user_id
WHERE u.user_id IN (SELECT DISTINCT user_id FROM water_bet_points)
GROUP BY u.user_id, u.display_name, u.total_points, u.singles_points, u.doubles_points;

-- Step 4: Update user points - deduct water bet points
UPDATE users u
SET 
    total_points = u.total_points - COALESCE((
        SELECT SUM(total_water_points) 
        FROM water_bet_points wbp 
        WHERE wbp.user_id = u.user_id
    ), 0),
    singles_points = u.singles_points - COALESCE((
        SELECT SUM(total_water_points) 
        FROM water_bet_points wbp 
        WHERE wbp.user_id = u.user_id AND wbp.match_type = 'SINGLES'
    ), 0),
    doubles_points = u.doubles_points - COALESCE((
        SELECT SUM(total_water_points) 
        FROM water_bet_points wbp 
        WHERE wbp.user_id = u.user_id AND wbp.match_type != 'SINGLES'
    ), 0),
    updated_at = NOW()
WHERE u.user_id IN (SELECT DISTINCT user_id FROM water_bet_points);

-- Step 5: Show count of matches to be deleted
SELECT 
    COUNT(*) as total_water_matches,
    SUM(CASE WHEN status = 'APPROVED' THEN 1 ELSE 0 END) as approved_matches,
    SUM(CASE WHEN status = 'PENDING' THEN 1 ELSE 0 END) as pending_matches,
    SUM(CASE WHEN status = 'REJECTED' THEN 1 ELSE 0 END) as rejected_matches
FROM match_reports 
WHERE stake_value = 2;

-- Step 6: Delete match_players records for water bets (due to foreign key)
DELETE FROM match_players 
WHERE match_id IN (SELECT match_id FROM water_bet_matches);

-- Step 7: Delete match_reports with stake_value = 2
DELETE FROM match_reports 
WHERE stake_value = 2;

-- Show final summary
SELECT 'Deletion complete' as status, 
       (SELECT COUNT(*) FROM match_reports WHERE stake_value = 2) as remaining_water_bets;

-- Verify no negative points
SELECT user_id, display_name, total_points, singles_points, doubles_points
FROM users
WHERE total_points < 0 OR singles_points < 0 OR doubles_points < 0;

COMMIT;

-- If you want to rollback, run: ROLLBACK;
