import { ApiProperty } from '@nestjs/swagger';
import { BaseDto } from '@lib/common';

export class SignInResponseDto extends BaseDto<SignInResponseDto> {
  @ApiProperty({
    example: '3644da06-0415-4b23-ac08-4c218cb41aa3',
    description: 'User token',
  })
  readonly token: string;
}
