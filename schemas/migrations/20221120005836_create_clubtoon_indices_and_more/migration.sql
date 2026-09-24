-- CreateIndex
CREATE INDEX "Club_nameRequestId_idx" ON "Club"("nameRequestId");

-- CreateIndex
CREATE INDEX "ClubToon_clubId_idx" ON "ClubToon"("clubId");

-- CreateIndex
CREATE INDEX "ClubToon_requestedAt_idx" ON "ClubToon" USING BRIN ("requestedAt" timestamp_minmax_multi_ops);

-- CreateIndex
CREATE INDEX "ClubToon_joinedAt_idx" ON "ClubToon" USING BRIN ("joinedAt" timestamp_minmax_multi_ops);

-- CreateIndex
CREATE INDEX "ClubToon_updatedAt_idx" ON "ClubToon" USING BRIN ("updatedAt" timestamp_minmax_multi_ops);

-- CreateIndex
CREATE INDEX "ClubToon_deletedAt_idx" ON "ClubToon" USING BRIN ("deletedAt" timestamp_minmax_multi_ops);
