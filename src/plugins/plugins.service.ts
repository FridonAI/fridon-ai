import { Injectable } from '@nestjs/common';
import { Plugin, PluginsRepository } from './plugins.repository';

@Injectable()
export class PluginsService {
  constructor(private readonly pluginRepository: PluginsRepository) {}

  setPlugins(plugins: Plugin[]): void {
    this.pluginRepository.set(plugins);
  }

  getPlugins(): Plugin[] {
    return this.pluginRepository.findAll();
  }
}
