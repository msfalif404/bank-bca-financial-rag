from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from openinference.instrumentation.litellm import LiteLLMInstrumentor

_is_telemetry_setup = False

def setup_telemetry(endpoint="http://localhost:6006/v1/traces"):
    """
    Sets up OpenTelemetry tracing and exports it to Arize Phoenix.
    Also instruments LiteLLM calls automatically.
    """
    global _is_telemetry_setup
    if _is_telemetry_setup:
        return
        
    try:
        # Hanya set provider jika belum ada (mencegah double-setup di Streamlit)
        if not isinstance(trace.get_tracer_provider(), TracerProvider):
            provider = TracerProvider()
            exporter = OTLPSpanExporter(endpoint=endpoint)
            provider.add_span_processor(BatchSpanProcessor(exporter))
            trace.set_tracer_provider(provider)
            
        # Instrument LiteLLM untuk mendapatkan visibilitas prompt dan response
        LiteLLMInstrumentor().instrument()
        
        _is_telemetry_setup = True
        print("✅ Observability (Arize Phoenix & OpenTelemetry) is enabled.")
        
    except Exception as e:
        print(f"⚠️ Warning: Failed to set up observability: {e}")
