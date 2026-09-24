CREATE INDEX "ClubLog_data" ON "ClubLog" USING GIN ("data");
CREATE INDEX "ClubLog_clubId" ON "ClubLog" ("clubId");
CREATE INDEX "ClubLog_logType" ON "ClubLog" ("logType");
CREATE INDEX "ClubLog_createdAt" ON "ClubLog" USING BRIN ("createdAt");