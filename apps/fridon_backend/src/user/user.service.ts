import { HttpException, HttpStatus, Injectable } from '@nestjs/common';
import { Prisma } from '@prisma/client';
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

  async getWalletVerification(walletAddress: string) {
    return await this.prisma.walletVerification.findUnique({
      where: {
        walletId: walletAddress,
      },
    });
  }

  async verifyUser(walletAddress: string, txId: string, amount: number) {
    let verificationSucceeded = false;

    try {
      await this.prisma.walletVerification.upsert({
        where: {
          walletId: walletAddress,
          verified: false,
        },
        update: {
          txId: txId,
          verified: true,
          amount: amount,
          updatedAt: new Date(),
        },
        create: {
          walletId: walletAddress,
          txId: txId,
          verified: true,
          amount: amount,
          createdAt: new Date(),
          updatedAt: new Date(),
        },
      });
      verificationSucceeded = true;
    } catch (e) {
      console.log(e);

      if (e instanceof Prisma.PrismaClientKnownRequestError) {
        if (e.code === 'P2002') {
          throw new HttpException(
            'User already verified',
            HttpStatus.BAD_REQUEST,
          );
        }
      }

      throw new HttpException(
        'Failed to verify user',
        HttpStatus.INTERNAL_SERVER_ERROR,
      );
    } finally {
      // Send the verification status regardless of success or failure
      this.eventsService.sendTo(walletAddress, 'user.user-verified', {
        walletId: walletAddress,
        verified: verificationSucceeded,
      });
    }
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
