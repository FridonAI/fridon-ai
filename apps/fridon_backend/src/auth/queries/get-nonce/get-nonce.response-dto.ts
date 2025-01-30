import { BaseDto } from '@lib/common';
import { ApiProperty } from '@nestjs/swagger';

export class GetNonceResponseDto extends BaseDto<GetNonceResponseDto> {
  @ApiProperty({
    example: '',
    description: 'User nonce',
  })
  readonly nonce: string;

  @ApiProperty({
    example: '',
    description: 'verifiedAt',
  })
  readonly verifiedAt?: string | undefined;
}
