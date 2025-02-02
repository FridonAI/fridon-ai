import { BaseDto } from "@lib/common";

export class BonkNotificationsMessageDto extends BaseDto<BonkNotificationsMessageDto> {
  type: string;
  source: string;
  extension: string;
  id: string;
  name: string;
  path: string;
  url: string;
}