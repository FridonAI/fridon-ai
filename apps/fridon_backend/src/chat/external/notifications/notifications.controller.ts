import { Controller, Logger } from '@nestjs/common';
import {
  NotificationResponseGeneratedMessageDto,
  NotificationsMessageUpdateDto,
} from './notifications.dto';
import { EventPattern } from '@nestjs/microservices';
import { PrismaService } from 'nestjs-prisma';
import { randomUUID } from 'crypto';
import { MessageType } from '@prisma/client';
import { EventsService } from 'src/events/events.service';

@Controller()
export class NotificationsEventsController {
  private logger = new Logger(NotificationsEventsController.name);

  constructor(
    private readonly prisma: PrismaService,
    private readonly eventsService: EventsService,
  ) {}

  @EventPattern('notifications_received')
  async messageUpdateEventHandler(
    event: NotificationsMessageUpdateDto,
  ): Promise<void> {
    console.log('event', JSON.stringify(event));

    const timestamp = new Date().toISOString();

    const { walletId, slug, message } = event;

    // 1) Using slug Query all the user who has this plugin.
    const walletPlugins = await this.prisma.walletPlugin.findMany({
      where: {
        pluginId: slug,
        ...(walletId ? { walletId: walletId } : {}),
      },
      select: {
        walletId: true,
      },
    });

    const walletIds = walletPlugins.map((plugin) => plugin.walletId);

    console.log('walletIds', walletIds);

    // 2) For each user check if they have chat id already for notifications or create it.
    const chatNotifications = await this.prisma.chatNotifications.findMany({
      where: {
        walletId: { in: walletIds },
      },
    });

    const existingWalletIds = chatNotifications.map(
      (notification) => notification.walletId,
    );

    console.log('existingWalletIds', existingWalletIds);
    const newWalletIds = walletIds.filter(
      (walletId) => !existingWalletIds.includes(walletId),
    );

    console.log('newWalletIds', newWalletIds);
    const newChatNotifications = newWalletIds.map((walletId) => ({
      walletId,
      chatId: randomUUID() as string,
    }));

    if (newChatNotifications.length > 0) {
      await this.prisma.chatNotifications.createMany({
        data: newChatNotifications,
      });
    }

    const notifications = [
      ...chatNotifications.map((notification) => ({
        walletId: notification.walletId,
        chatId: notification.chatId,
      })),
      ...newChatNotifications.map((notification) => ({
        walletId: notification.walletId,
        chatId: notification.chatId,
      })),
    ];

    // // Update message to chat--> chatMessage
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
              content: message,
              messageType: MessageType.Notification,
              createdAt: timestamp,
            },
          },
          walletId,
        },
        update: {
          messages: {
            create: {
              id: messageId,
              content: message,
              messageType: MessageType.Notification,
              createdAt: timestamp,
            },
          },
        },
      });

      // 3) Send the ws notification to the user.
      this.logger.log(
        `Sent batch notification to wallets ${walletId}: ${message}`,
      );

      this.eventsService.sendTo(
        walletId,
        'chat.response-generated',
        new NotificationResponseGeneratedMessageDto({
          type: 'notification',
          id: messageId,
          message: message,
          chatId: 'notifications',
          date: timestamp,
          name: slug
            .split('-')
            .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
            .join(' '),
          imageUrl:
            'https://fridon-ai-assets.s3.eu-central-1.amazonaws.com/agent-avatars/bonkheadog.png',
        }),
      );
    }
  }
}
