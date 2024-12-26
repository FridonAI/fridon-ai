import { Injectable } from '@nestjs/common';
import { Plugin, PluginsRepository } from './plugins.repository';
import { PrismaService } from 'nestjs-prisma';

@Injectable()
export class PluginsService {
  constructor(
    private readonly pluginRepository: PluginsRepository,
    private readonly prisma: PrismaService,
  ) {}

  setPlugins(plugins: Plugin[]): void {
    this.pluginRepository.set(plugins);
  }

  getPlugins(): Plugin[] {
    return this.pluginRepository.findAll();
  }

  get(slug: string): Plugin | undefined {
    const plugins = this.pluginRepository.findAll();
    return plugins.find((plugin) => plugin.slug === slug);
  }

  getDefaultPlugins(): Plugin[] {
    const defaultPluginSlugs = [
      'solana-bonk-educator',
      'coin-technical-analyzer',
      'coin-technical-chart-searcher',
      'coin-observer',
      'emperor-trading',
      'fridon',
      'wallet',
      'jupiter',
    ];

    return this.pluginRepository
      .findAll()
      .filter((plugin) => defaultPluginSlugs.includes(plugin.slug));
  }

  getFreePlugins(): Plugin[] {
    return this.pluginRepository
      .findAll()
      .filter((plugin) => plugin.price === 0);
  }

  getPluginOwner(id: string): string {
    const plugin = this.get(id);
    if (!plugin) {
      throw new Error(`Plugin[${id}] not found`);
    }

    return plugin.owner;
  }

  async getSubscribersCount(pluginId: string): Promise<number> {
    const res = await this.prisma.walletPlugin.count({
      where: { pluginId },
    });

    return res;
  }
}
