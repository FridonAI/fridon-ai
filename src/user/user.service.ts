import { Injectable } from '@nestjs/common';
import { WalletPlugin } from '@prisma/client';
import { PrismaService } from 'nestjs-prisma';
// import { PrismaService } from 'nestjs-prisma';

export type AssignPluginDto = {
  walletId: string;
  pluginId: string;
  expiresAt: Date;
};

@Injectable()
export class UserService {
  constructor(private readonly prisma: PrismaService) {}

  getUserPlugins(walletAddress: string): Promise<WalletPlugin[]> {
    const res = this.prisma.walletPlugin.findMany({
      where: {
        walletId: walletAddress,
        expiresAt: { gte: new Date() },
      },
    });

    return res;
  }

  async assignPlugin(body: AssignPluginDto) {
    this.prisma.walletPlugin.upsert({
      where: {
        walletId_pluginId: { walletId: body.walletId, pluginId: body.pluginId },
      },
      create: {
        expiresAt: body.expiresAt,
        pluginId: body.pluginId,
        walletId: body.walletId,
      },
      update: {
        expiresAt: body.expiresAt,
      },
    });
  }
}
