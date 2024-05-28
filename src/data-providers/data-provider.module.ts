import { Module } from '@nestjs/common';
import { DataProviderController } from './data-provider.controller';
import { DataProviderService } from './data-provider.service';

@Module({
  imports: [],
  providers: [DataProviderService],
  controllers: [DataProviderController],
})
export class DataProviderModule {}
