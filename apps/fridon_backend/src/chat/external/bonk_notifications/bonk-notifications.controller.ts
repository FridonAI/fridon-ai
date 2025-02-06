import { Controller, Logger } from '@nestjs/common';
import { EventPattern } from '@nestjs/microservices';
import {
  BonkNotificationResponseGeneratedMessageDto,
  BonkNotificationsMessageDto,
} from './bonk-notifications.dto';
import { PrismaService } from 'nestjs-prisma';
import { EventsService } from 'src/events/events.service';
import { randomUUID } from 'crypto';
import { MessageType } from '@prisma/client';

@Controller()
export class BonkNotificationsController {
  private logger = new Logger(BonkNotificationsController.name);

  constructor(
    private readonly prisma: PrismaService,
    private readonly eventsService: EventsService,
  ) {}

  @EventPattern('bonk_notifier')
  async handleBonkNotifier(events: BonkNotificationsMessageDto[]) {
    console.log('events', JSON.stringify(events));

    const timestamp = new Date().toISOString();

    const walletPlugins = await this.prisma.walletPlugin.findMany({
      where: {
        pluginId: 'bonk-notifier',
      },
      select: {
        walletId: true,
      },
    });

    const walletIds = walletPlugins.map((plugin) => plugin.walletId);

    console.log('walletIds', walletIds);

    const bonkNotifications = await this.prisma.bonkNotifications.findMany({
      where: {
        walletId: { in: walletIds },
      },
    });

    const existingWalletIds = bonkNotifications.map(
      (notification) => notification.walletId,
    );

    console.log('existingWalletIds', existingWalletIds);

    const newWalletIds = walletIds.filter(
      (id) => !existingWalletIds.includes(id),
    );

    console.log('newWalletIds', newWalletIds);

    const newBonkNotifications = newWalletIds.map((walletId) => ({
      walletId,
      chatId: randomUUID() as string,
    }));

    if (newBonkNotifications.length > 0) {
      await this.prisma.bonkNotifications.createMany({
        data: newBonkNotifications,
      });
    }

    const notifications = [
      ...bonkNotifications.map((notification) => ({
        walletId: notification.walletId,
        chatId: notification.chatId,
      })),
      ...newBonkNotifications.map((notification) => ({
        walletId: notification.walletId,
        chatId: notification.chatId,
      })),
    ];

    for (const walletId of walletIds) {
      const chatId = notifications.find(
        (notification) => notification.walletId === walletId,
      )?.chatId;

      if (!chatId) {
        this.logger.warn(`No chatId found for walletId ${walletId}`);
        throw new Error(`No chatId found for walletId ${walletId}`);
      }

      const messageId = randomUUID() as string;

      await this.prisma.chat.upsert({
        where: { id: chatId },
        create: {
          id: chatId,
          messages: {
            create: {
              id: messageId,
              content: '',
              structuredData: JSON.stringify(
                events.map((event) => JSON.stringify(event)),
              ),
              messageType: MessageType.BonkNotification,
              createdAt: timestamp,
            },
          },
          walletId,
          chatType: 'Regular',
        },
        update: {
          messages: {
            create: {
              id: messageId,
              content: '',
              structuredData: JSON.stringify(
                events.map((event) => JSON.stringify(event)),
              ),
              messageType: MessageType.BonkNotification,
              createdAt: timestamp,
            },
          },
        },
      });

      this.logger.log(
        `Sent bonk notification to wallet ${walletId}: ${JSON.stringify(events)}`,
      );

      this.eventsService.sendTo(
        walletId,
        'chat.response-generated',
        new BonkNotificationResponseGeneratedMessageDto({
          type: 'bonk-notification',
          id: messageId,
          chatId: 'bonk-notifications',
          date: timestamp,
          structuredMessages: events.map((event) => JSON.stringify(event)),
        }),
      );
    }
  }
}
