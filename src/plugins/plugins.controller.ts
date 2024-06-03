import { Controller, Get } from '@nestjs/common';
import { PluginsService } from './plugins.service';
import { ApiTags } from '@nestjs/swagger';

@Controller('plugins')
@ApiTags('plugins')
export class PluginsController {
  constructor(private readonly pluginService: PluginsService) {}

  @Get()
  findAll() {
    return this.pluginService.getPlugins();
  }
}
