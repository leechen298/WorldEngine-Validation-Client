import { useEffect, useMemo, useRef } from "react";
import { Application, Container, Graphics } from "pixi.js";

interface TilePayload {
  x?: number;
  y?: number;
  terrain?: string;
  color?: string;
}

interface EntityPayload {
  id?: string;
  x?: number;
  y?: number;
  sprite?: string;
}

interface PixelWorldCanvasProps {
  visualization?: Record<string, unknown>;
}

function readItems<T>(visualization: Record<string, unknown> | undefined, key: string): T[] {
  const value = visualization?.[key];
  return Array.isArray(value) ? (value.filter((item) => typeof item === "object" && item !== null) as T[]) : [];
}

function hasFinitePosition(item: TilePayload | EntityPayload): item is Required<Pick<TilePayload, "x" | "y">> & typeof item {
  return Number.isFinite(item.x) && Number.isFinite(item.y);
}

function terrainColor(tile: TilePayload): number {
  if (typeof tile.color === "string" && /^#[0-9a-f]{6}$/i.test(tile.color)) {
    return Number.parseInt(tile.color.slice(1), 16);
  }
  if (tile.terrain === "water") {
    return 0x4da3ff;
  }
  if (tile.terrain === "stone") {
    return 0x8d99ae;
  }
  return 0x5ec269;
}

export function PixelWorldCanvas({ visualization }: PixelWorldCanvasProps) {
  const canvasHostRef = useRef<HTMLDivElement | null>(null);
  const tiles = useMemo(() => readItems<TilePayload>(visualization, "tiles").filter(hasFinitePosition), [visualization]);
  const entities = useMemo(
    () => readItems<EntityPayload>(visualization, "entities").filter(hasFinitePosition),
    [visualization],
  );
  const hasVisualization = tiles.length > 0 || entities.length > 0;

  useEffect(() => {
    const host = canvasHostRef.current;
    if (!host || !hasVisualization) {
      return;
    }

    let app: Application | null = null;
    let cancelled = false;

    async function draw() {
      app = new Application();
      await app.init({ backgroundAlpha: 0, height: 280, width: 360 });
      if (cancelled || !host) {
        app.destroy();
        return;
      }
      host.replaceChildren(app.canvas);
      const layer = new Container();
      app.stage.addChild(layer);

      for (const tile of tiles) {
        const x = tile.x;
        const y = tile.y;
        const graphic = new Graphics();
        graphic.rect(x * 28, y * 28, 28, 28).fill(terrainColor(tile));
        layer.addChild(graphic);
      }

      for (const entity of entities) {
        const x = entity.x;
        const y = entity.y;
        const graphic = new Graphics();
        graphic.circle(x * 28 + 14, y * 28 + 14, 8).fill(entity.sprite === "person" ? 0xffd166 : 0xf77f00);
        layer.addChild(graphic);
      }
    }

    void draw();

    return () => {
      cancelled = true;
      app?.destroy();
    };
  }, [entities, hasVisualization, tiles]);

  return (
    <section className="page-card canvas-box">
      <h3>公开像素地图</h3>
      {hasVisualization ? (
        <>
          <div ref={canvasHostRef} aria-label="公开可视化画布" className="pixel-canvas-host" />
          <p className="canvas-meta">
            tiles {tiles.length} / entities {entities.length}
          </p>
        </>
      ) : (
        <p>暂无公开可视化数据。</p>
      )}
    </section>
  );
}
