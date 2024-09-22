import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useOpportunities, usePositions } from "./lib/api";
import Opportunity from "./components/opportunity";
import Position from "./components/position";

export default function App() {
	const { data: opportunities } = useOpportunities();
	const { data: positions } = usePositions();
	return (
		<div className="dark bg-background text-foreground w-screen h-screen p-12 gap-6 flex flex-col">
			<Card>
				<CardHeader>
					<CardTitle>Opportunities</CardTitle>
				</CardHeader>
				<CardContent className="flex flex-row gap-3">
					{opportunities?.map((o, i) => (
						<Opportunity key={i} opportunity={o} index={i} />
					))}
				</CardContent>
			</Card>
			<Card>
				<CardHeader>
					<CardTitle>Positions</CardTitle>
				</CardHeader>
				<CardContent className="flex flex-row gap-3">
					{positions?.map((p, i) => (
						<Position key={i} position={p} index={i} />
					))}
				</CardContent>
			</Card>
		</div>
	);
}
