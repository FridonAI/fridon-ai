import { BaseDto } from '@lib/common';
import { NotificationType } from './notifications.type';
import { ApiProperty } from '@nestjs/swagger';
import { OffsetPaginatedResponseDto } from '@lib/common/dtos/offset-paginated-response.base';

// Find Notifications Response DTO
export class FindNotificationsDto extends BaseDto<FindNotificationsDto> {
  walletId: string;
  type: NotificationType;
  text: string;
  read: boolean;
  createdAt: number;
  updatedAt: number;
}

export class FindNotificationsResponseDto extends OffsetPaginatedResponseDto<FindNotificationsDto> {
  @ApiProperty({ type: FindNotificationsDto, isArray: true })
  declare readonly data: readonly FindNotificationsDto[];
}

// Find Notifications Count Response DTO
export class FindNotificationsCountResponseDto extends BaseDto<FindNotificationsCountResponseDto> {
  @ApiProperty({
    example: {
      [NotificationType.Alert]: 0,
      [NotificationType.System]: 0,
    },
  })
  count: Record<NotificationType, number>;
}
