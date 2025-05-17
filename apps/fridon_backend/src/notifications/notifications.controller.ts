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
  DisableAlertRequestDto,
  FindNotificationsRequestDto,
  ReadNotificationRequestDto,
} from './notifications.request.dto';
import {
  FindNotificationsQueryResult,
  NotificationsRepository,
} from './notifications.repository';
import { Wallet, WalletSession } from '@lib/auth';
import { Request } from 'express';
import {
  AlertSettingResponseDto,
  CreateAlertSettingResponseDto,
  CreateNotificationResponseDto,
  DisableAlertSettingResponseDto,
  FindAlertSettingResponseDto,
  FindNotificationsCountResponseDto,
  FindNotificationsDto,
  FindNotificationsResponseDto,
} from './notifications.response.dto';
import { Notification } from '@prisma/client';
import { NotificationType } from './notifications.type';
// import { EventsService } from 'src/events/events.service';
import { EventPattern } from '@nestjs/microservices';
import { EventsService } from 'src/events/events.service';

@Controller('notifications')
export class NotificationsController {
  private logger = new Logger(NotificationsController.name);

  constructor(
    private readonly notificationsRepository: NotificationsRepository,
    private readonly eventsService: EventsService,
  ) {}

  @Post('read')
  async readNotification(
    @Wallet() wallet: WalletSession,
    @Body() body: ReadNotificationRequestDto,
  ) {
    this.logger.log('readNotification', JSON.stringify(body));
    const walletId = wallet.walletAddress;
    return await this.notificationsRepository.readNotification(
      body.notificationId,
      walletId,
    );
  }

  @Post('read-all')
  async readAllNotifications(@Wallet() wallet: WalletSession) {
    this.logger.log('readAllNotifications');
    const walletId = wallet.walletAddress;
    return await this.notificationsRepository.readAllNotifications(walletId);
  }

  @Post('disable-alert')
  async disableAlert(
    @Wallet() wallet: WalletSession,
    @Body() body: DisableAlertRequestDto,
  ) {
    this.logger.log('disableAlert', JSON.stringify(body));
    const walletId = wallet.walletAddress;

    await this.notificationsRepository.disableAlertSetting(
      body.alertId,
      walletId,
    );

    this.eventsService.sendTo(
      walletId,
      'notification.disable-alert',
      new DisableAlertSettingResponseDto({
        type: 'disable-alert',
        id: body.alertId,
        walletId,
      }),
    );
  }

  @EventPattern('create-alert')
  async createAlert(
    createAlertRequestDto: CreateAlertRequestDto,
  ): Promise<string> {
    this.logger.log('createAlert', JSON.stringify(createAlertRequestDto));
    const { alertId, walletId, text } = createAlertRequestDto;

    this.eventsService.sendTo(
      walletId,
      'notification.create-alert',
      new CreateAlertSettingResponseDto({
        type: 'create-alert',
        id: alertId,
        walletId,
        text,
      }),
    );

    return await this.notificationsRepository.createAlertSetting(
      alertId,
      walletId,
      text,
    );
  }

  @EventPattern('create-notification')
  async createNotification(
    @Body() createNotificationRequestDto: CreateNotificationRequestDto,
  ) {
    this.logger.log(
      'createNotification',
      JSON.stringify(createNotificationRequestDto),
    );
    const { walletId, type, text } = createNotificationRequestDto;

    this.eventsService.sendTo(
      walletId,
      'notification.create-notification',
      new CreateNotificationResponseDto({
        type: 'create-notification',
        notificationType: type,
        text,
        walletId,
      }),
    );
    return await this.notificationsRepository.createNotification(
      walletId,
      type,
      text,
    );
  }

  @Get('alert-settings')
  async getAlertSettings(@Wallet() wallet: WalletSession) {
    this.logger.log('getAlertSettings');
    const walletId = wallet.walletAddress;
    const result =
      await this.notificationsRepository.findAlertSettings(walletId);

    return new FindAlertSettingResponseDto({
      data: result.map((alertSetting) => {
        return new AlertSettingResponseDto({
          walletId: alertSetting.walletId,
          enabled: alertSetting.enabled,
          text: alertSetting.text,
          createdAt: alertSetting.createdAt.getDate(),
          updatedAt: alertSetting.updatedAt.getDate(),
        });
      }),
    });
  }

  @Get('count')
  async getNotificationsCount(@Wallet() wallet: WalletSession) {
    const notificationsCount =
      await this.notificationsRepository.findNotificationsCount(
        wallet.walletAddress,
      );

    return new FindNotificationsCountResponseDto({
      count: notificationsCount,
    });
  }

  @Get('all')
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
      id: result.id,
      walletId: result.walletId,
      type: result.type as NotificationType,
      text: result.text,
      read: result.read,
      createdAt: result.createdAt.getDate(),
      updatedAt: result.updatedAt.getDate(),
    });
  }
}
