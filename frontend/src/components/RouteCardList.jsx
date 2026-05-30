import RouteCard from "./RouteCard";

export default function RouteCardList({ routes = [] }) {
  const worstCost = routes.length > 0
    ? routes[routes.length - 1].total_cost_usd
    : 0;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
      {routes.map((route, i) => (
        <RouteCard
          key={`${route.method_name}-${i}`}
          route={route}
          worstCost={worstCost}
          index={i}
        />
      ))}
    </div>
  );
}
