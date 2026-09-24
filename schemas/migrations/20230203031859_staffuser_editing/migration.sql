-- CreateEnum
CREATE TYPE "StaffUserLogType" AS ENUM ('STAFF_EDITED');

-- AlterTable
ALTER TABLE "StaffUser" ADD COLUMN     "isEnabled" BOOLEAN NOT NULL DEFAULT true;

-- CreateTable
CREATE TABLE "StaffUserLog" (
    "id" SERIAL NOT NULL,
    "staffUserId" INTEGER,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "createdById" INTEGER NOT NULL,
    "logType" "StaffUserLogType" NOT NULL,
    "notes" TEXT NOT NULL,

    CONSTRAINT "StaffUserLog_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE INDEX "StaffUserLog_staffUserId_idx" ON "StaffUserLog"("staffUserId");

-- CreateIndex
CREATE INDEX "StaffUserLog_createdById_idx" ON "StaffUserLog"("createdById");

-- CreateIndex
CREATE INDEX "StaffUserLog_logType_idx" ON "StaffUserLog"("logType");

-- CreateIndex
CREATE INDEX "StaffUserLog_createdAt_idx" ON "StaffUserLog" USING BRIN ("createdAt" timestamp_minmax_multi_ops);

-- AddForeignKey
ALTER TABLE "StaffUserLog" ADD CONSTRAINT "StaffUserLog_staffUserId_fkey" FOREIGN KEY ("staffUserId") REFERENCES "StaffUser"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "StaffUserLog" ADD CONSTRAINT "StaffUserLog_createdById_fkey" FOREIGN KEY ("createdById") REFERENCES "StaffUser"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
