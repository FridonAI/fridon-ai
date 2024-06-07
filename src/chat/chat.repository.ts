import { Injectable } from '@nestjs/common';
import { ChatId } from './domain/chat-id.value-object';
import { PrismaService } from 'nestjs-prisma';
import { Prisma } from '@prisma/client';

@Injectable()
export class ChatRepository {
  constructor(private readonly prisma: PrismaService) {}

  async getChats(walletId: string) {
    const chats = await this.prisma.chat.findMany({
      where: { walletId },
      include: { messages: { orderBy: { createdAt: 'asc' }, take: 1 } },
    });

    return chats;
  }

  async getChatHistory(walletId: string, limit: number) {
    const chats = await this.prisma.chat.findMany({
      where: { walletId },
      include: {
        messages: {
          orderBy: {
            createdAt: 'asc',
          },
          take: limit,
        },
      },
      orderBy: {
        createdAt: 'asc',
      },
    });

    return chats;
  }

  async createChat(chatId: ChatId, walletId: string): Promise<void> {
    await this.prisma.chat.create({
      data: { id: chatId.value, walletId },
    });
  }

  async getChat(chatId: ChatId) {
    const chat = await this.prisma.chat.findUniqueOrThrow({
      where: { id: chatId.value },
      include: { messages: { orderBy: { createdAt: 'desc' } } },
    });

    return chat;
  }

  async createChatMessage(
    chatMessagePrisma: Prisma.ChatMessageCreateArgs['data'],
  ): Promise<void> {
    await this.prisma.chatMessage.create({ data: chatMessagePrisma });
  }
}
