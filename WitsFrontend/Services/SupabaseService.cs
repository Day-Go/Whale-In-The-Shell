using Supabase.Gotrue;

public class SupabaseService
{
    private readonly Client _supabaseClient;

    public SupabaseService(string url, string apiKey)
    {
        _supabaseClient = new Client(new ClientOptions
        {
            Url = url,
            Headers = new Dictionary<string, string>{
                {"api_key", apiKey} 
            }
        });
    }
}
