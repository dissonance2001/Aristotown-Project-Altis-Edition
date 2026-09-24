/*
  Warnings:

  - The values [CLUB_TASK_PURCHASED,CLUB_TASK_FAILED] on the enum `ClubLogType` will be removed. If these variants are still used in the database, this will fail.
  - You are about to drop the column `clubTask` on the `Club` table. All the data in the column will be lost.
  - You are about to drop the column `offeredClubTasks` on the `Club` table. All the data in the column will be lost.

*/
-- AlterEnum
BEGIN;
CREATE TYPE "ClubLogType_new" AS ENUM ('CLUB_CREATED', 'JOINED_CLUB', 'LEFT_CLUB', 'INVITED_TO_CLUB', 'ACCEPTED_CLUB_JOIN_INVITATION', 'KICKED_FROM_CLUB', 'USER_RANK_CHANGED', 'SETTINGS_UPDATED', 'LEADER_TRANSFERRED', 'EARNED_JELLYBEANS', 'EARNED_CLUB_XP', 'CLUB_PROMOTED', 'BOUGHT_ITEM', 'USED_ITEM', 'CLUB_NAME_APPROVED', 'CLUB_NAME_REJECTED', 'CLUB_NAME_SUBMITTED', 'CLUB_TASK_COMPLETE', 'CLUB_TASK_REROLLED', 'CLUB_OWNER_TRANSFERRED', 'CLUB_FORCE_OWNER_TRANSFERRED', 'CLUB_DISBANDED', 'CLUB_FORCE_DISBANDED');
ALTER TABLE "ClubLog" ALTER COLUMN "logType" TYPE "ClubLogType_new" USING ("logType"::text::"ClubLogType_new");
ALTER TYPE "ClubLogType" RENAME TO "ClubLogType_old";
ALTER TYPE "ClubLogType_new" RENAME TO "ClubLogType";
DROP TYPE "ClubLogType_old";
COMMIT;

-- AlterTable
ALTER TABLE "Club" DROP COLUMN "clubTask",
DROP COLUMN "offeredClubTasks",
ADD COLUMN     "clubTasks" JSONB[];
