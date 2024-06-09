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

  async getSubscribersCount(pluginId: string): Promise<number> {
    const res = await this.prisma.walletPlugin.count({
      where: { pluginId },
    });

    return res;
  }
}
