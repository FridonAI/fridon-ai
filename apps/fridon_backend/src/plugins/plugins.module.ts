import { Global, Module } from '@nestjs/common';
import { PluginsService } from './plugins.service';
import { PluginsController } from './plugins.controller';
import { PluginsRepository } from './plugins.repository';
import { PluginsEventListener } from './event-handlers/plugins-updated.redis-event-handler';

@Global()
@Module({
  providers: [PluginsService, PluginsRepository],
  controllers: [PluginsController, PluginsEventListener],
  exports: [PluginsService],
})
export class PluginsModule {}
