import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useOpportunities, usePositions } from "./lib/api";
import Opportunity from "./components/opportunity";
import Position from "./components/position";
import { useEffect } from 'react';
import { toast } from 'sonner';

export default function App() {
	const { data: opportunities, error: oppErr } = useOpportunities();
	const { data: positions, error: posErr } = usePositions();

	useEffect(() => {
		if (typeof oppErr !== 'undefined') {
			console.error(oppErr);
			toast.error(JSON.stringify(oppErr));
		}
	}, [oppErr]);

	useEffect(() => {
		if (typeof posErr !== 'undefined') {
			console.error(posErr);
			toast.error(JSON.stringify(posErr));
		}
	}, [posErr]);

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
