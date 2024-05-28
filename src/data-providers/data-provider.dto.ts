import { ApiProperty } from '@nestjs/swagger';
import { IsObject, IsString } from 'class-validator';

export class DataProviderRequestBodyDto {
  @IsString()
  @ApiProperty({ example: 'get-blockhash' })
  action: string;

  @IsObject()
  @ApiProperty({ example: { key: 'value' } })
  data: object;
}

export class DataProviderResponseBodyDto {
  @IsString()
  data: object;
}
