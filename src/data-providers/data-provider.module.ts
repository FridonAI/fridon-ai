import { Module } from '@nestjs/common';
import { DataProviderController } from './data-provider.controller';
import { DataProviderService } from './data-provider.service';
import { RegistryService } from './registry';
import { DiscoveryModule } from '@nestjs/core';

@Module({
  imports: [DiscoveryModule],
  providers: [DataProviderService, RegistryService],
  controllers: [DataProviderController],
})
export class DataProviderModule {}
