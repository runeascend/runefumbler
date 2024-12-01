import { CheckIcon } from "lucide-react";
import { Button } from "./ui/button";
import {
	Card,
	CardContent,
	CardFooter,
	CardHeader,
	CardTitle,
} from "./ui/card";
import { Cross1Icon } from "@radix-ui/react-icons";
import { z } from "zod";
import { opportunitySchema, useActionMutation } from "@/lib/api";
import dayjs from "dayjs";

export interface OpportunityProps {
	index: number;
	opportunity: z.infer<typeof opportunitySchema>;
}

export default function Opportunity(props: OpportunityProps) {
	const { mutateAsync: buyOpp } = useActionMutation("buy", props.index);
	const { mutateAsync: deleteOpp } = useActionMutation(
		"delete_opportunity",
		props.index,
	);

	return (
		<Card className="grow">
			<CardHeader>
				<CardTitle>{props.opportunity.name}</CardTitle>
			</CardHeader>
			<CardContent>
				<div className="flex flex-row justify-between">
					<span>Buy</span>
					<span>
{props.opportunity.buy}
					</span>
				</div>
				B: 
				<br />
				S: {props.opportunity.sell}
				<br />
				T: {props.opportunity.time}
			</CardContent>
			<CardFooter className="gap-1.5">
				<Button size="icon" onClick={() => buyOpp()}>
					<CheckIcon className="w-5 h-5" />
				</Button>
				<Button
					size="icon"
					onClick={() => deleteOpp()}
					variant="destructive"
				>
					<Cross1Icon className="w-5 h-5" />
				</Button>
			</CardFooter>
		</Card>
	);
}
