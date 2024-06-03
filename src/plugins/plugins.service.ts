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

  get(name: string): Plugin | null {
    const plugins = this.pluginRepository.findAll();
    return plugins.find((plugin) => plugin.name === name);
  }
}
