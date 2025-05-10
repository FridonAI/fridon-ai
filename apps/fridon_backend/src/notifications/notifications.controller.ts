import {
  Body,
  Controller,
  Get,
  Logger,
  Post,
  Query,
  Req,
} from '@nestjs/common';
import {
  CreateAlertRequestDto,
  CreateNotificationRequestDto,
  FindNotificationsRequestDto,
} from './notifications.request.dto';
import {
  FindNotificationsQueryResult,
  NotificationsRepository,
} from './notifications.repository';
import { Wallet, WalletSession } from '@lib/auth';
import { Request } from 'express';
import {
  FindNotificationsCountResponseDto,
  FindNotificationsDto,
  FindNotificationsResponseDto,
} from './notifications.response.dto';
import { Notification } from '@prisma/client';
import { NotificationType } from './notifications.type';

@Controller('notifications')
export class NotificationsController {
  private logger = new Logger(NotificationsController.name);

  constructor(
    private readonly notificationsRepository: NotificationsRepository,
  ) {}

  @Post('create-alert')
  async createAlert(
    @Body() createAlertRequestDto: CreateAlertRequestDto,
  ): Promise<string> {
    this.logger.log('createAlert', JSON.stringify(createAlertRequestDto));
    const { alertId, walletId, text } = createAlertRequestDto;
    return await this.notificationsRepository.createAlertSetting(
      alertId,
      walletId,
      text,
    );
  }

  @Post('create-notification')
  async createNotification(
    @Body() createNotificationRequestDto: CreateNotificationRequestDto,
  ) {
    this.logger.log(
      'createNotification',
      JSON.stringify(createNotificationRequestDto),
    );
    const { walletId, type, text } = createNotificationRequestDto;

    return await this.notificationsRepository.createNotification(
      walletId,
      type,
      text,
    );
  }

  async getNotificationsCount(@Wallet() wallet: WalletSession) {
    const notificationsCount =
      await this.notificationsRepository.findNotificationsCount(
        wallet.walletAddress,
      );

    return new FindNotificationsCountResponseDto({
      count: notificationsCount,
    });
  }

  @Get('get-all')
  async getNotifications(
    @Wallet() wallet: WalletSession,
    @Req() req: Request,
    @Query() query: FindNotificationsRequestDto,
  ) {
    const walletId = wallet.walletAddress;
    const result: FindNotificationsQueryResult =
      await this.notificationsRepository.findNotifications({
        pagination: {
          page: query.page ?? 1,
          limit: query.limit ?? 10,
        },
        filters: {
          type: query.type,
          unread: query.unread,
          walletId,
        },
        sort: query.sortBy
          ? {
              by: query.sortBy,
              order: query.sortOrder ?? 'asc',
            }
          : undefined,
      });

    return this.formatOutput(req, result);
  }

  private formatOutput(
    req: Request,
    result: FindNotificationsQueryResult,
  ): FindNotificationsResponseDto {
    return new FindNotificationsResponseDto({
      page: result.page,
      limit: result.limit,
      total: result.total,

      firstPage: result.firstPage,
      prevPage: result.prevPage,
      nextPage: result.nextPage,
      lastPage: result.lastPage,

      firstPageUrl: this.updatePageUrl(req, result.firstPage),
      prevPageUrl: result.prevPage
        ? this.updatePageUrl(req, result.prevPage)
        : null,
      nextPageUrl: result.nextPage
        ? this.updatePageUrl(req, result.nextPage)
        : null,
      lastPageUrl: this.updatePageUrl(req, result.lastPage),

      data: result.data.map((notification) =>
        this.formatOutputTournaments(notification),
      ),
    });
  }

  private updatePageUrl(req: Request, page: number): string {
    const currentUrlRaw = 'https://' + req.get('host') + req.originalUrl;

    const url = new URL(currentUrlRaw);
    url.searchParams.set('page', `${page}`);

    return url.href;
  }

  private formatOutputTournaments(result: Notification): FindNotificationsDto {
    return new FindNotificationsDto({
      walletId: result.walletId,
      type: result.type as NotificationType,
      text: result.text,
      read: result.read,
      createdAt: result.createdAt.getDate(),
      updatedAt: result.updatedAt.getDate(),
    });
  }
}
