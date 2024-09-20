import { Body, Controller, Post } from '@nestjs/common';
import { ApiTags } from '@nestjs/swagger';
import {
  DataProviderRequestBodyDto,
  DataProviderResponseBodyDto,
} from './data-provider.dto';
import { DataProviderService } from './data-provider.service';

@Controller('data')
@ApiTags('data')
export class DataProviderController {
  constructor(private readonly service: DataProviderService) {}

  @Post('/executor')
  async get(
    @Body() body: DataProviderRequestBodyDto,
  ): Promise<DataProviderResponseBodyDto> {
    console.log('body', body);

    const data = await this.service.resolve(
      `${body.plugin}-${body.function}`,
      body.args,
    );

    return { data: data };
  }
}
