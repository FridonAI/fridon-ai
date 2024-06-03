import { Controller, Logger } from '@nestjs/common';
import { EventPattern } from '@nestjs/microservices';
import { PluginsService } from '../plugins.service';

// ToDo: add correct typing
export type PluginDto = {
  name: string;
};

@Controller()
export class PluginsEventListener {
  constructor(private readonly pluginService: PluginsService) {}

  @EventPattern('plugins')
  async process(event: PluginDto[]): Promise<void> {
    const currentPlugins = this.pluginService.getPlugins();
    const newPlugins = event;

    if (currentPlugins.length !== newPlugins.length) {
      Logger.log('Plugins updated: ' + JSON.stringify(newPlugins));
    }

    this.pluginService.setPlugins(newPlugins);
  }
}
