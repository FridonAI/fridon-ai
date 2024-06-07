import { Injectable } from '@nestjs/common';
import { WalletPlugin } from '@prisma/client';
import { PrismaService } from 'nestjs-prisma';
import { EventsService } from 'src/events/events.service';
// import { PrismaService } from 'nestjs-prisma';

export type AssignPluginDto = {
  walletId: string;
  pluginId: string;
  expiresAt: Date;
};

@Injectable()
export class UserService {
  constructor(
    private readonly prisma: PrismaService,
    private readonly eventsService: EventsService,
  ) {}

  async getUserPlugins(walletAddress: string): Promise<WalletPlugin[]> {
    const res = await this.prisma.walletPlugin.findMany({
      where: {
        walletId: walletAddress,
        expiresAt: { gte: new Date() },
      },
    });

    return res;
  }

  async assignPlugin(body: AssignPluginDto) {
    await this.prisma.walletPlugin.upsert({
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

    // todo: call sendTo method.
    this.eventsService.sendTo(body.walletId, 'user.plugin-assigned', {
      pluginId: body.pluginId,
      expiresAt: body.expiresAt,
    });
  }
}
