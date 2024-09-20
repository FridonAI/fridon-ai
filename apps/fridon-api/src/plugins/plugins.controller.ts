import { Controller, Get, UseInterceptors } from '@nestjs/common';
import { PluginsService } from './plugins.service';
import { ApiTags } from '@nestjs/swagger';
import { FindAllPluginsDtoResponseDto } from './plugins.dto';
import { CacheInterceptor, CacheTTL } from '@nestjs/cache-manager';

@Controller('plugins')
@ApiTags('plugins')
@UseInterceptors(CacheInterceptor)
export class PluginsController {
  constructor(private readonly pluginService: PluginsService) {}

  @CacheTTL(5) // ToDo: Change to 30 seconds
  @Get()
  async findAll(): Promise<FindAllPluginsDtoResponseDto[]> {
    const plugins = this.pluginService.getPlugins();

    const res = Promise.all(
      plugins.map(async (plugin) => ({
        ...plugin,
        subscribersCount: await this.pluginService.getSubscribersCount(
          plugin.slug,
        ),
      })),
    );

    return res;
  }
}
