import * as Prisma from '@prisma/client';
import { Wallet } from '../domain/wallet';

type WalletDb = Prisma.Wallet;

export class AuthMapper {
  toDomain(wallet: WalletDb) {
    return new Wallet({
      walletAddress: wallet.walletAddress,
      nonce: wallet.nonce,
      userType: wallet.userType ?? undefined,
      expirationTime: wallet.expirationTime ?? undefined,
      verifiedAt: wallet.verifiedAt
        ? new Date(wallet.verifiedAt).toISOString()
        : undefined,
      createdAt: wallet.createdAt,
      updatedAt: wallet.updatedAt,
    });
  }
}
