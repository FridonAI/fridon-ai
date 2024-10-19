import { BaseDto } from '@lib/common';

export class NotificationsMessageUpdateDto {
  walletId?: string;
  slug: string;
  message: string;
}

export class NotificationResponseGeneratedMessageDto extends BaseDto<NotificationResponseGeneratedMessageDto> {
  type: 'notification';
  id: string;
  chatId: string;
  message: string;
  date: string;
  name: string;
  imageUrl?: string | undefined;
}
