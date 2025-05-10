import { Injectable } from '@nestjs/common';
import { Prisma, NotificationType, Notification } from '@prisma/client';
import { PrismaService } from 'nestjs-prisma';
import { availableSorts } from './notifications.request.dto';

export type OffsetPaginatedResponse<T> = {
  page: number;
  limit: number;
  firstPage: number;
  nextPage: number | null;
  prevPage: number | null;
  lastPage: number;
  total: number;
  data: T[];
};

export type NotificationsSortsKeyType = (typeof availableSorts)[number];

export type FindNotificationsProps = {
  pagination?: {
    page?: number;
    limit?: number;
  };
  filters?: {
    type?: NotificationType;
    unread?: boolean;
    walletId?: string;
  };
  sort?:
    | {
        by: NotificationsSortsKeyType;
        order: 'asc' | 'desc';
      }
    | undefined;
};
export type FindNotificationsQueryResult =
  OffsetPaginatedResponse<Notification>;

@Injectable()
export class NotificationsRepository {
  constructor(private readonly prisma: PrismaService) {}

  async createAlertSetting(
    alertId: string,
    walletId: string,
    text: string,
  ): Promise<string> {
    const alert = await this.prisma.alertSettings.create({
      data: {
        id: alertId,
        text,
        walletId,
        createdAt: new Date(),
        updatedAt: new Date(),
      },
      select: {
        id: true,
      },
    });

    return alert.id;
  }

  async createNotification(
    walletId: string,
    type: string,
    text: string,
  ): Promise<number> {
    const notification = await this.prisma.notification.create({
      data: {
        walletId,
        type: type as NotificationType,
        text,
        createdAt: new Date(),
        updatedAt: new Date(),
      },
      select: {
        id: true,
      },
    });

    return notification.id;
  }

  async findNotificationsCount(
    walletId: string,
  ): Promise<Record<NotificationType, number>> {
    // Loop over notifications type and get the count for each type
    const notificationsCount = await this.prisma.notification.groupBy({
      by: ['type'],
      where: {
        walletId,
        read: false,
      },
      _count: {
        type: true,
      },
    });
    const notificationsCountMap = notificationsCount.reduce(
      (acc, notification) => {
        acc[notification.type] = notification._count.type;
        return acc;
      },
      {} as Record<NotificationType, number>,
    );
    return notificationsCountMap;
  }

  async findNotifications(
    props?: FindNotificationsProps,
  ): Promise<FindNotificationsQueryResult> {
    const { pagination, filters, sort } = props ?? {};

    const where: Prisma.NotificationWhereInput = {};
    const whereAnd: Prisma.NotificationWhereInput[] = [];
    let orderBy: Prisma.NotificationFindManyArgs['orderBy'] = {};

    if (filters) {
      if (filters.walletId) {
        where.walletId = filters.walletId;
      }
      if (filters.type) {
        whereAnd.push({ type: filters.type });
      }
      if (filters.unread) {
        whereAnd.push({ read: false });
      }
    }

    if (sort) {
      if (availableSorts.includes(sort.by as NotificationsSortsKeyType)) {
        orderBy = { [sort.by]: sort.order };
      }
    }

    let { page, limit } = pagination ?? {};
    page ??= 1;
    limit ??= 10;

    const take = limit;
    const skip = (page - 1) * limit;

    const [result, count] = await this.prisma.$transaction([
      this.prisma.notification.findMany({
        take,
        skip,
        where,
        orderBy,
      }),
      this.prisma.notification.count({ where }),
    ]);

    return {
      page,
      limit,
      firstPage: 1,
      lastPage: Math.ceil(count / limit),
      prevPage: page === 1 ? null : page - 1,
      nextPage: result.length === limit ? page + 1 : null,
      data: result,
      total: count,
    };
  }
}
