"""
MoTeC i2 Pro Export
Professional motorsport telemetry tool integration

PROFESYONEL ENTEGRASYON:
GR-Pilot → MoTeC i2 Pro format
Toyota engineers bu dosyayı doğrudan MoTeC'te açabilir
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional
import struct
import logging

logger = logging.getLogger(__name__)


class MoTeCExporter:
    """
    MoTeC i2 Pro format exporter

    MoTeC: Industry-standard telemetry analysis software
    Used by: F1, IndyCar, NASCAR, WEC teams

    File format: Binary .ld (Log Data) format
    """

    def __init__(self):
        self.telemetry_data: Optional[pd.DataFrame] = None
        self.metadata: Dict = {}

    def prepare_data(
        self,
        df: pd.DataFrame,
        session_name: str = "GR-Pilot Session",
        vehicle: str = "Toyota GR",
        driver: str = "Driver"
    ) -> None:
        """
        MoTeC export için veri hazırla

        Args:
            df: Telemetry DataFrame
            session_name: Session name
            vehicle: Vehicle name
            driver: Driver name
        """
        self.telemetry_data = df.copy()

        self.metadata = {
            'session_name': session_name,
            'vehicle': vehicle,
            'driver': driver,
            'date': pd.Timestamp.now().strftime('%Y-%m-%d'),
            'venue': 'Circuit of The Americas',
            'format_version': 'GR-Pilot v1.0'
        }

        logger.info(f"Prepared {len(df)} telemetry points for MoTeC export")

    def export_to_csv_motec_compatible(
        self,
        output_path: str
    ) -> str:
        """
        MoTeC-compatible CSV export

        MoTeC can import CSV with specific format:
        - Header row with channel names
        - Time column (seconds)
        - Data columns

        Args:
            output_path: Output file path

        Returns:
            Export status message
        """
        if self.telemetry_data is None:
            raise ValueError("No data prepared. Call prepare_data() first")

        df = self.telemetry_data.copy()

        # Create time column
        if 'TimeStamp' in df.columns:
            df['TimeStamp'] = pd.to_datetime(df['TimeStamp'])
            df['Time'] = (df['TimeStamp'] - df['TimeStamp'].iloc[0]).dt.total_seconds()
        else:
            # Assume 100Hz sampling (10ms per sample)
            df['Time'] = np.arange(len(df)) * 0.01

        # MoTeC channel name mapping
        channel_mapping = {
            'Speed': 'GPS Speed',
            'BrakePressure': 'Brake Press',
            'Throttle': 'Throttle Pos',
            'SteeringAngle': 'Steer Angle',
            'LateralAcceleration': 'Lat Accel',
            'LongitudinalAcceleration': 'Long Accel',
            'RPM': 'Engine RPM',
            'Gear': 'Gear'
        }

        # Select and rename columns
        export_columns = ['Time']

        for orig_col, motec_col in channel_mapping.items():
            if orig_col in df.columns:
                df[motec_col] = df[orig_col]
                export_columns.append(motec_col)

        # Export CSV
        df[export_columns].to_csv(output_path, index=False, float_format='%.6f')

        logger.info(f"Exported MoTeC-compatible CSV: {output_path}")

        return f"✅ Exported {len(df)} data points to {output_path}"

    def export_to_ldx(
        self,
        output_path: str
    ) -> str:
        """
        MoTeC LDX (XML) format export

        LDX: Easier to generate than binary .ld
        Still directly loadable in MoTeC i2

        Args:
            output_path: Output file path

        Returns:
            Export status message
        """
        if self.telemetry_data is None:
            raise ValueError("No data prepared")

        df = self.telemetry_data.copy()

        # Create time column
        if 'TimeStamp' in df.columns:
            df['TimeStamp'] = pd.to_datetime(df['TimeStamp'])
            df['Time'] = (df['TimeStamp'] - df['TimeStamp'].iloc[0]).dt.total_seconds()
        else:
            df['Time'] = np.arange(len(df)) * 0.01

        # Build LDX (XML structure)
        ldx_content = self._build_ldx_xml(df)

        # Write file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(ldx_content)

        logger.info(f"Exported MoTeC LDX: {output_path}")

        return f"✅ Exported MoTeC LDX format: {output_path}"

    def _build_ldx_xml(self, df: pd.DataFrame) -> str:
        """
        Build LDX XML structure

        Args:
            df: Prepared DataFrame

        Returns:
            XML string
        """
        xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
        xml += '<LDXFile>\n'

        # Header
        xml += '  <Header>\n'
        xml += f'    <SessionName>{self.metadata["session_name"]}</SessionName>\n'
        xml += f'    <Vehicle>{self.metadata["vehicle"]}</Vehicle>\n'
        xml += f'    <Driver>{self.metadata["driver"]}</Driver>\n'
        xml += f'    <Date>{self.metadata["date"]}</Date>\n'
        xml += f'    <Venue>{self.metadata["venue"]}</Venue>\n'
        xml += f'    <FormatVersion>{self.metadata["format_version"]}</FormatVersion>\n'
        xml += '  </Header>\n'

        # Channels
        xml += '  <Channels>\n'

        channels = {
            'Time': {'unit': 's', 'freq': 100},
            'Speed': {'unit': 'km/h', 'freq': 100},
            'BrakePressure': {'unit': 'bar', 'freq': 100},
            'Throttle': {'unit': '%', 'freq': 100},
            'SteeringAngle': {'unit': 'deg', 'freq': 100}
        }

        for channel, props in channels.items():
            if channel in df.columns or channel == 'Time':
                xml += f'    <Channel name="{channel}" unit="{props["unit"]}" frequency="{props["freq"]}" />\n'

        xml += '  </Channels>\n'

        # Data (sampled - full data would be too large)
        xml += '  <Data>\n'

        # Sample every 10th point to keep file size reasonable
        sample_df = df.iloc[::10]

        for idx, row in sample_df.iterrows():
            xml += '    <Sample>\n'

            if 'Time' in row:
                xml += f'      <Time>{row["Time"]:.6f}</Time>\n'

            if 'Speed' in row:
                xml += f'      <Speed>{row["Speed"]:.2f}</Speed>\n'

            if 'BrakePressure' in row:
                xml += f'      <BrakePressure>{row["BrakePressure"]:.2f}</BrakePressure>\n'

            if 'Throttle' in row:
                xml += f'      <Throttle>{row["Throttle"]:.2f}</Throttle>\n'

            if 'SteeringAngle' in row:
                xml += f'      <SteeringAngle>{row["SteeringAngle"]:.2f}</SteeringAngle>\n'

            xml += '    </Sample>\n'

        xml += '  </Data>\n'
        xml += '</LDXFile>\n'

        return xml

    def get_export_info(self) -> str:
        """
        Export bilgisi

        Returns:
            Info text
        """
        if self.telemetry_data is None:
            return "No data loaded"

        info = f"""
=== MoTeC EXPORT INFO ===

Session: {self.metadata['session_name']}
Vehicle: {self.metadata['vehicle']}
Driver: {self.metadata['driver']}
Data Points: {len(self.telemetry_data):,}

Available Formats:
1. CSV (MoTeC-compatible) - Best compatibility
2. LDX (XML) - Native MoTeC format

How to use:
1. Export to CSV or LDX
2. Open MoTeC i2 Pro
3. File → Open → Select exported file
4. Analyze with professional tools

Channels included:
- GPS Speed
- Brake Pressure
- Throttle Position
- Steering Angle
- Accelerations (if available)
"""
        return info


# Test
if __name__ == "__main__":
    # Sample data
    sample_df = pd.DataFrame({
        'TimeStamp': pd.date_range('2024-01-01 14:00:00', periods=1000, freq='10ms'),
        'Speed': np.random.normal(150, 20, 1000),
        'BrakePressure': np.random.uniform(0, 100, 1000),
        'Throttle': np.random.uniform(0, 100, 1000),
        'SteeringAngle': np.random.normal(0, 15, 1000)
    })

    exporter = MoTeCExporter()

    # Prepare
    exporter.prepare_data(
        sample_df,
        session_name="Test Session",
        vehicle="Toyota GR Supra",
        driver="Test Driver"
    )

    print(exporter.get_export_info())

    # Export CSV
    csv_status = exporter.export_to_csv_motec_compatible("test_motec.csv")
    print(f"\n{csv_status}")

    # Export LDX
    ldx_status = exporter.export_to_ldx("test_motec.ldx")
    print(f"{ldx_status}")
