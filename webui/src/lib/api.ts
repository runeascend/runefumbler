import { z } from "zod";
import {
	queryOptions,
	useQuery,
	useMutation,
	useQueryClient,
} from "@tanstack/react-query";

const API_URL = "http://localhost:12346";

interface GETRequest<O extends z.ZodTypeAny> {
	method: "GET";
	endpoint: string;
	schema: O;
}

interface POSTRequest<O extends z.ZodTypeAny, I = undefined> {
	method: "POST";
	endpoint: string;
	body?: I;
	schema: O;
}

interface DELETERequest<O extends z.ZodTypeAny> {
	method: "DELETE";
	endpoint: string;
	schema: O;
}

async function request<O extends z.ZodTypeAny, I = undefined>(
	r: GETRequest<O> | POSTRequest<O, I> | DELETERequest<O>,
): Promise<z.infer<O>> {
	const resp = await fetch(new URL(r.endpoint, API_URL), {
		method: r.method,
		body: r.method === "POST" ? JSON.stringify(r.body) : undefined,
	});

	const body = await resp.json();
	return r.schema.parse(body);
}

export const opportunitySchema = z.object({
	name: z.string(),
	buy: z.number(),
	sell: z.number(),
	time: z.number(),
	ttl: z.number(),
});

export const positionSchema = z.object({
	buy_coord: z.tuple([z.number(), z.number()]),
	sell_coord: z.tuple([z.number(), z.number()]),
	state: z.string(),
	name: z.string(),
	buy_price: z.number(),
	sell_price: z.number(),
});

export const positionsQuery = queryOptions({
	queryKey: ["positions"],
	queryFn: async () =>
		request({
			method: "GET",
			endpoint: "/positions",
			schema: z.array(positionSchema),
		}),
});

export function usePositions() {
	return useQuery(positionsQuery);
}

export const opportunitiesQuery = queryOptions({
	queryKey: ["opportunity"],
	queryFn: async () =>
		request({
			method: "GET",
			endpoint: "/opportunities",
			schema: z.array(opportunitySchema),
		}),
});

export function useOpportunities() {
	return useQuery(opportunitiesQuery);
}

export function useActionMutation(
	action: "buy" | "delete_opportunity" | "sell" | "collect" | "exit",
	n: number,
) {
	const qc = useQueryClient();
	return useMutation({
		mutationFn: async () =>
			request({
				method: "POST",
				endpoint: `/${action}/${n}`,
				schema: z.undefined(),
			}),
		onMutate() {
			qc.invalidateQueries(opportunitiesQuery);
			qc.invalidateQueries(positionsQuery);
		},
	});
}
