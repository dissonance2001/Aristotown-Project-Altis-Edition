-- DropIndex
DROP INDEX "ClubLog_createdAt";

-- DropIndex
DROP INDEX "ClubLog_data";

-- CreateIndex
CREATE INDEX "Club_createdAt_idx" ON "Club" USING BRIN ("createdAt" timestamp_minmax_multi_ops);

-- CreateIndex
CREATE INDEX "Club_updatedAt_idx" ON "Club" USING BRIN ("updatedAt" timestamp_minmax_multi_ops);

-- CreateIndex
CREATE INDEX "Club_deletedAt_idx" ON "Club" USING BRIN ("deletedAt" timestamp_minmax_multi_ops);

-- CreateIndex
CREATE INDEX "ClubInfraction_clubId_idx" ON "ClubInfraction"("clubId");

-- CreateIndex
CREATE INDEX "ClubInfraction_createdById_idx" ON "ClubInfraction"("createdById");

-- CreateIndex
CREATE INDEX "ClubInfraction_infractionType_idx" ON "ClubInfraction"("infractionType");

-- CreateIndex
CREATE INDEX "ClubInfraction_createdAt_idx" ON "ClubInfraction" USING BRIN ("createdAt" timestamp_minmax_multi_ops);

-- CreateIndex
CREATE INDEX "ClubLog_createdAt_idx" ON "ClubLog" USING BRIN ("createdAt" timestamp_minmax_multi_ops);

-- CreateIndex
CREATE INDEX "ClubModerationLog_clubId_idx" ON "ClubModerationLog"("clubId");

-- CreateIndex
CREATE INDEX "ClubModerationLog_clubInfractionId_idx" ON "ClubModerationLog"("clubInfractionId");

-- CreateIndex
CREATE INDEX "ClubModerationLog_createdById_idx" ON "ClubModerationLog"("createdById");

-- CreateIndex
CREATE INDEX "ClubModerationLog_logType_idx" ON "ClubModerationLog"("logType");

-- CreateIndex
CREATE INDEX "ClubModerationLog_createdAt_idx" ON "ClubModerationLog" USING BRIN ("createdAt" timestamp_minmax_multi_ops);

-- RenameIndex
ALTER INDEX "ClubLog_clubId" RENAME TO "ClubLog_clubId_idx";

-- RenameIndex
ALTER INDEX "ClubLog_logType" RENAME TO "ClubLog_logType_idx";
