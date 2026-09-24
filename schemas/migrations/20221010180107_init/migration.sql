CREATE EXTENSION pg_trgm;
CREATE EXTENSION btree_gin;

-- CreateEnum
CREATE TYPE "ClubNameStatus" AS ENUM ('NAME_REQUESTED', 'NAME_APPROVED', 'NAME_DENIED', 'NAME_FAILED', 'NAME_CHANGING');

-- CreateEnum
CREATE TYPE "ClubInfractionType" AS ENUM ('WARNING', 'MUTE', 'JOIN_LOCK', 'MOTD_EDIT_LOCK', 'DISBAND');

-- CreateEnum
CREATE TYPE "ClubLogType" AS ENUM ('CLUB_CREATED', 'JOINED_CLUB', 'LEFT_CLUB', 'INVITED_TO_CLUB', 'ACCEPTED_CLUB_JOIN_INVITATION', 'KICKED_FROM_CLUB', 'USER_RANK_CHANGED', 'SETTINGS_UPDATED', 'LEADER_TRANSFERRED', 'EARNED_JELLYBEANS', 'EARNED_CLUB_XP', 'CLUB_PROMOTED', 'BOUGHT_ITEM', 'USED_ITEM', 'CLUB_NAME_APPROVED', 'CLUB_NAME_REJECTED', 'CLUB_NAME_SUBMITTED', 'CLUB_TASK_PURCHASED', 'CLUB_TASK_COMPLETE', 'CLUB_TASK_FAILED', 'CLUB_TASK_REROLLED', 'CLUB_OWNER_TRANSFERRED', 'CLUB_FORCE_OWNER_TRANSFERRED', 'CLUB_DISBANDED', 'CLUB_FORCE_DISBANDED');

-- CreateEnum
CREATE TYPE "ClubModerationLogType" AS ENUM ('INFRACTION', 'INFO');

-- CreateTable
CREATE TABLE "StaffUser" (
    "id" SERIAL NOT NULL,
    "name" TEXT NOT NULL,
    "email" TEXT NOT NULL,
    "googleAccessToken" TEXT NOT NULL,
    "googleRefreshToken" TEXT NOT NULL,
    "googleIdToken" TEXT NOT NULL,
    "profilePicture" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "groups" TEXT[],

    CONSTRAINT "StaffUser_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Club" (
    "id" SERIAL NOT NULL,
    "name" TEXT NOT NULL,
    "requestedName" TEXT,
    "nameRequestId" INTEGER,
    "nameStatus" "ClubNameStatus" NOT NULL DEFAULT 'NAME_REQUESTED',
    "ownerAccountId" INTEGER NOT NULL,
    "ownerAvId" INTEGER NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "deletedAt" TIMESTAMP(3),
    "clubIcon" JSONB NOT NULL,
    "motd" TEXT,
    "capacity" INTEGER NOT NULL,
    "maxBoosters" INTEGER NOT NULL DEFAULT 1,
    "level" INTEGER NOT NULL DEFAULT 1,
    "dailyCoins" INTEGER NOT NULL,
    "clubXp" INTEGER NOT NULL,
    "clubCoins" DOUBLE PRECISION NOT NULL,
    "jellybeans" INTEGER NOT NULL,
    "clubSettings" JSONB,
    "boosters" JSONB[],
    "ownedItems" INTEGER[],
    "clubTask" JSONB,
    "offeredClubTasks" JSONB[],

    CONSTRAINT "Club_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "ClubToon" (
    "id" SERIAL NOT NULL,
    "clubId" INTEGER NOT NULL,
    "avId" INTEGER NOT NULL,
    "invitedBy" INTEGER NOT NULL,
    "requestedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "joinedAt" TIMESTAMP(3),
    "updatedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "deletedAt" TIMESTAMP(3),
    "rankId" INTEGER,

    CONSTRAINT "ClubToon_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "ClubLog" (
    "id" SERIAL NOT NULL,
    "clubId" INTEGER NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "logType" "ClubLogType" NOT NULL,
    "data" JSONB NOT NULL,

    CONSTRAINT "ClubLog_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "ClubInfraction" (
    "id" SERIAL NOT NULL,
    "clubId" INTEGER NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "createdById" INTEGER NOT NULL,
    "infractionType" "ClubInfractionType" NOT NULL,
    "expiresAt" TIMESTAMP(3),
    "repealedAt" TIMESTAMP(3),
    "reason" TEXT NOT NULL,
    "supportingEvidence" TEXT NOT NULL DEFAULT '',

    CONSTRAINT "ClubInfraction_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "ClubModerationLog" (
    "id" SERIAL NOT NULL,
    "clubId" INTEGER NOT NULL,
    "clubInfractionId" INTEGER,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "createdById" INTEGER NOT NULL,
    "logType" "ClubModerationLogType" NOT NULL,
    "notes" TEXT NOT NULL,

    CONSTRAINT "ClubModerationLog_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "StaffUser_email_key" ON "StaffUser"("email");

-- CreateIndex
CREATE UNIQUE INDEX "Club_nameRequestId_key" ON "Club"("nameRequestId");

-- CreateIndex
CREATE INDEX "ClubToon_avId_idx" ON "ClubToon"("avId");

-- CreateIndex
CREATE UNIQUE INDEX "ClubToon_clubId_avId_key" ON "ClubToon"("clubId", "avId");

-- AddForeignKey
ALTER TABLE "ClubToon" ADD CONSTRAINT "ClubToon_clubId_fkey" FOREIGN KEY ("clubId") REFERENCES "Club"("id") ON DELETE RESTRICT ON UPDATE CASCADE DEFERRABLE INITIALLY DEFERRED;

-- AddForeignKey
ALTER TABLE "ClubLog" ADD CONSTRAINT "ClubLog_clubId_fkey" FOREIGN KEY ("clubId") REFERENCES "Club"("id") ON DELETE RESTRICT ON UPDATE CASCADE DEFERRABLE INITIALLY DEFERRED;

-- AddForeignKey
ALTER TABLE "ClubInfraction" ADD CONSTRAINT "ClubInfraction_clubId_fkey" FOREIGN KEY ("clubId") REFERENCES "Club"("id") ON DELETE RESTRICT ON UPDATE CASCADE DEFERRABLE INITIALLY DEFERRED;

-- AddForeignKey
ALTER TABLE "ClubInfraction" ADD CONSTRAINT "ClubInfraction_createdById_fkey" FOREIGN KEY ("createdById") REFERENCES "StaffUser"("id") ON DELETE RESTRICT ON UPDATE CASCADE DEFERRABLE INITIALLY DEFERRED;

-- AddForeignKey
ALTER TABLE "ClubModerationLog" ADD CONSTRAINT "ClubModerationLog_clubId_fkey" FOREIGN KEY ("clubId") REFERENCES "Club"("id") ON DELETE RESTRICT ON UPDATE CASCADE DEFERRABLE INITIALLY DEFERRED;

-- AddForeignKey
ALTER TABLE "ClubModerationLog" ADD CONSTRAINT "ClubModerationLog_clubInfractionId_fkey" FOREIGN KEY ("clubInfractionId") REFERENCES "ClubInfraction"("id") ON DELETE SET NULL ON UPDATE CASCADE DEFERRABLE INITIALLY DEFERRED;

-- AddForeignKey
ALTER TABLE "ClubModerationLog" ADD CONSTRAINT "ClubModerationLog_createdById_fkey" FOREIGN KEY ("createdById") REFERENCES "StaffUser"("id") ON DELETE RESTRICT ON UPDATE CASCADE DEFERRABLE INITIALLY DEFERRED;

CREATE INDEX "Club_name_fulltext_index"
  ON "Club" USING GIN (to_tsvector('english', name));
