import { Injectable } from '@nestjs/common';
import { ChatId } from './domain/chat-id.value-object';
import { PrismaService } from 'nestjs-prisma';
import { Prisma } from '@prisma/client';

@Injectable()
export class ChatRepository {
  constructor(private readonly prisma: PrismaService) {}

  async getChatNotifications(walletId: string) {
    const chatId = await this.prisma.chatNotifications.findUnique({
      where: { walletId },
    });

    if (!chatId) {
      return undefined;
    }

    const notificationChat = await this.prisma.chat.findUnique({
      where: {
        id: chatId.chatId,
      },
      include: {
        messages: {
          orderBy: { createdAt: 'desc' },
        },
      },
    });

    return notificationChat;
  }

  async getChats(walletId: string, chatType: 'Regular' | 'SuperChart') {
    const chats = await this.prisma.chat.findMany({
      where: { walletId, chatType },
      include: {
        messages: { orderBy: { createdAt: 'asc' }, take: 1 },
        rectangle: true,
      },
    });

    return chats;
  }

  async getChatHistory(walletId: string, limit: number) {
    const messages = await this.prisma.chatMessage.findMany({
      where: {
        Chat: {
          walletId: walletId,
        },
        messageType: 'Query',
      },
      orderBy: {
        createdAt: 'desc',
      },
      take: limit,
      include: {
        Chat: {
          include: {
            rectangle: true,
          },
        },
      },
    });

    return messages;
  }

  async createChat(chatId: ChatId, walletId: string, rectanglePrisma?: Prisma.RectangleCreateArgs['data']): Promise<void> {
    let rectangleId: string | undefined;

    if (rectanglePrisma) {
      const rectangle = await this.prisma.rectangle.create({
        data: rectanglePrisma,
      });
      rectangleId = rectangle.id;
    }

    await this.prisma.chat.create({
      data: {
        id: chatId.value,
        walletId,
        rectangleId,
        chatType: rectangleId ? 'SuperChart' : 'Regular',
      },
    });
  }

  async getChat(chatId: ChatId) {
    const chat = await this.prisma.chat.findUniqueOrThrow({
      where: { id: chatId.value },
      include: { messages: { orderBy: { createdAt: 'desc' } }, rectangle: true },
    });

    return chat;
  }

  async createChatMessage(
    chatMessagePrisma: Prisma.ChatMessageCreateArgs['data'],
  ): Promise<void> {
    await this.prisma.chatMessage.create({ data: chatMessagePrisma });
  }

  async updateChatMessage(messageId: string, pluginsUsed: string[]) {
    await this.prisma.chatMessage.update({
      where: { id: messageId },
      data: {
        plugins: pluginsUsed,
      },
    });
  }
}
