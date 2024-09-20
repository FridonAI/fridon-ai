import { Injectable } from '@nestjs/common';
import { PrismaService } from 'nestjs-prisma';
import { EventsService } from 'src/events/events.service';
import { PluginsService } from 'src/plugins/plugins.service';
// import { PrismaService } from 'nestjs-prisma';

export type AssignPluginDto = {
  walletId: string;
  pluginId: string;
  expiresAt: Date;
};

export type UserPluginsResponseDto = {
  id: string;
  expiresAt: Date | null;
}[];

@Injectable()
export class UserService {
  constructor(
    private readonly prisma: PrismaService,
    private readonly eventsService: EventsService,
    private readonly pluginsService: PluginsService,
  ) {}

  async getUserPlugins(walletAddress: string): Promise<UserPluginsResponseDto> {
    const res = await this.prisma.walletPlugin.findMany({
      where: {
        walletId: walletAddress,
        expiresAt: { gte: new Date() },
      },
    });

    const freePlugins = this.pluginsService.getDefaultPlugins();

    const result: UserPluginsResponseDto = [
      ...res.map((plugin) => ({
        id: plugin.pluginId,
        expiresAt: plugin.expiresAt,
      })),
      ...freePlugins.map((plugin) => ({
        id: plugin.slug,
        expiresAt: null,
      })),
    ];

    return result;
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
