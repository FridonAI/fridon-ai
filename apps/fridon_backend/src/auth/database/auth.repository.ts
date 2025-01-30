import { Injectable } from '@nestjs/common';
import * as crypto from 'crypto';
import { PrismaService } from 'nestjs-prisma';
import { AuthMapper } from './auth.mapper';

export const generateRandomNonce = () => {
  const prefix = 'Defiland Mobile Authorization Token';
  const randomHex = crypto.randomBytes(16).toString('hex');
  return `${prefix}: ${randomHex}`;
};

@Injectable()
export class AuthRepository {
  constructor(
    private prisma: PrismaService,
    private mapper: AuthMapper,
  ) {}

  async getNonce(walletAddress: string) {
    const wallet = await this.prisma.wallet.findUnique({
      where: {
        walletAddress,
      },
    });

    if (!wallet) {
      return undefined;
    }

    return this.mapper.toDomain(wallet);
  }

  async createNonce(walletAddress: string, ExpirationTtlSeconds = 120) {
    return await this.prisma.wallet.create({
      data: {
        walletAddress,
        nonce: generateRandomNonce(),
        expirationTime: Math.floor(Date.now() / 1000) + ExpirationTtlSeconds,
        createdAt: new Date(),
        updatedAt: new Date(),
      },
    });
  }

  async updateNonce(walletAddress: string) {
    const nonce = generateRandomNonce();
    await this.prisma.wallet.update({
      where: {
        walletAddress,
      },
      data: {
        nonce: nonce,
        updatedAt: new Date(),
      },
    });
  }

  async verifyWallet(walletAddress: string) {
    await this.prisma.wallet.update({
      where: {
        walletAddress,
      },
      data: {
        verifiedAt: new Date(),
        expirationTime: null,
        updatedAt: new Date(),
      },
    });
  }
}
