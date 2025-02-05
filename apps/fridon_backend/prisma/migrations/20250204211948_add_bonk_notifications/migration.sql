-- AlterEnum
ALTER TYPE "MessageType" ADD VALUE 'BonkNotification';

-- CreateTable
CREATE TABLE "BonkNotifications" (
    "id" SERIAL NOT NULL,
    "walletId" TEXT NOT NULL,
    "chatId" UUID NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "BonkNotifications_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "BonkNotifications_walletId_key" ON "BonkNotifications"("walletId");

-- CreateIndex
CREATE UNIQUE INDEX "BonkNotifications_chatId_key" ON "BonkNotifications"("chatId");
