-- CreateEnum
CREATE TYPE "NotificationType" AS ENUM ('System', 'Alert');

-- CreateTable
CREATE TABLE "Notification" (
    "id" SERIAL NOT NULL,
    "walletId" TEXT NOT NULL,
    "type" "NotificationType" NOT NULL,
    "text" TEXT NOT NULL,
    "read" BOOLEAN NOT NULL DEFAULT false,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "Notification_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "AlertSettings" (
    "id" TEXT NOT NULL,
    "walletId" TEXT NOT NULL,
    "enabled" BOOLEAN NOT NULL DEFAULT true,
    "text" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "AlertSettings_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE INDEX "Notification_walletId_type_idx" ON "Notification"("walletId", "type");

-- CreateIndex
CREATE INDEX "Notification_walletId_read_idx" ON "Notification"("walletId", "read");
