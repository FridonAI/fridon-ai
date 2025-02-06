-- CreateTable
CREATE TABLE "WalletVerification" (
    "id" SERIAL NOT NULL,
    "walletId" TEXT NOT NULL,
    "verified" BOOLEAN NOT NULL DEFAULT false,
    "txId" TEXT,
    "amount" DOUBLE PRECISION,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "WalletVerification_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "WalletVerification_walletId_key" ON "WalletVerification"("walletId");
