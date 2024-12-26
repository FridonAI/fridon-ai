-- CreateEnum
CREATE TYPE "MessageType" AS ENUM ('Query', 'Response', 'TransactionResponse', 'Notification');

-- CreateEnum
CREATE TYPE "ChatType" AS ENUM ('Regular', 'SuperChart');

-- CreateTable
CREATE TABLE "ChatMessage" (
    "id" UUID NOT NULL,
    "content" TEXT NOT NULL,
    "messageType" "MessageType" NOT NULL,
    "structuredData" TEXT,
    "personality" TEXT,
    "plugins" TEXT[],
    "chatId" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "ChatMessage_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Rectangle" (
    "id" TEXT NOT NULL,
    "symbol" TEXT NOT NULL,
    "startDate" TIMESTAMP(3) NOT NULL,
    "endDate" TIMESTAMP(3) NOT NULL,
    "startPrice" DOUBLE PRECISION NOT NULL,
    "endPrice" DOUBLE PRECISION NOT NULL,
    "interval" TEXT NOT NULL,

    CONSTRAINT "Rectangle_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Chat" (
    "id" TEXT NOT NULL,
    "walletId" TEXT NOT NULL,
    "chatType" "ChatType" NOT NULL,
    "rectangleId" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "Chat_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "ChatNotifications" (
    "id" SERIAL NOT NULL,
    "walletId" TEXT NOT NULL,
    "chatId" UUID NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "ChatNotifications_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "WalletMedia" (
    "walletId" TEXT NOT NULL,
    "mediaId" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "WalletMedia_pkey" PRIMARY KEY ("walletId","mediaId")
);

-- CreateTable
CREATE TABLE "Media" (
    "id" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "Media_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "WalletScoreHistory" (
    "id" SERIAL NOT NULL,
    "walletId" TEXT NOT NULL,
    "chatId" TEXT NOT NULL,
    "score" INTEGER NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "WalletScoreHistory_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Leaderboard" (
    "walletId" TEXT NOT NULL,
    "score" DOUBLE PRECISION NOT NULL,
    "pluginsUsed" DOUBLE PRECISION NOT NULL,
    "myPluginsUsed" DOUBLE PRECISION NOT NULL,
    "transactionsMade" DOUBLE PRECISION NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "Leaderboard_pkey" PRIMARY KEY ("walletId")
);

-- CreateTable
CREATE TABLE "WalletPlugin" (
    "walletId" TEXT NOT NULL,
    "pluginId" TEXT NOT NULL,
    "expiresAt" TIMESTAMP(3) NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "WalletPlugin_pkey" PRIMARY KEY ("walletId","pluginId")
);

-- CreateIndex
CREATE INDEX "ChatMessage_chatId_idx" ON "ChatMessage"("chatId");

-- CreateIndex
CREATE UNIQUE INDEX "Chat_rectangleId_key" ON "Chat"("rectangleId");

-- CreateIndex
CREATE INDEX "Chat_walletId_idx" ON "Chat"("walletId");

-- CreateIndex
CREATE UNIQUE INDEX "ChatNotifications_walletId_key" ON "ChatNotifications"("walletId");

-- CreateIndex
CREATE UNIQUE INDEX "ChatNotifications_chatId_key" ON "ChatNotifications"("chatId");

-- CreateIndex
CREATE INDEX "WalletMedia_mediaId_idx" ON "WalletMedia"("mediaId");

-- CreateIndex
CREATE INDEX "WalletMedia_walletId_idx" ON "WalletMedia"("walletId");

-- CreateIndex
CREATE INDEX "Leaderboard_walletId_score_idx" ON "Leaderboard"("walletId", "score");

-- CreateIndex
CREATE INDEX "Leaderboard_score_idx" ON "Leaderboard"("score");

-- AddForeignKey
ALTER TABLE "ChatMessage" ADD CONSTRAINT "ChatMessage_chatId_fkey" FOREIGN KEY ("chatId") REFERENCES "Chat"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Chat" ADD CONSTRAINT "Chat_rectangleId_fkey" FOREIGN KEY ("rectangleId") REFERENCES "Rectangle"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "WalletMedia" ADD CONSTRAINT "WalletMedia_mediaId_fkey" FOREIGN KEY ("mediaId") REFERENCES "Media"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
