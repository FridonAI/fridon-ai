-- AlterEnum
ALTER TYPE "MessageType" ADD VALUE 'Notification';

-- CreateTable
CREATE TABLE "ChatNotifications" (
    "id" SERIAL NOT NULL,
    "walletId" TEXT NOT NULL,
    "chatId" UUID NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "ChatNotifications_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "ChatNotifications_walletId_key" ON "ChatNotifications"("walletId");

-- CreateIndex
CREATE UNIQUE INDEX "ChatNotifications_chatId_key" ON "ChatNotifications"("chatId");
