import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert'; // For JSON encoding/decoding
import 'package:google_fonts/google_fonts.dart'; // For Space Mono font

// --- Constants (mirroring Python) ---
const double DEFAULT_RISK_PERCENT = 1.000;
const double MIN_LEVERAGE = 1.000;
const double MIN_REWARD_RISK_RATIO = 2.000;

// IMPORTANT: Replace with your actual API server URL
// If running locally, ensure your mobile device/emulator can reach your computer's IP
// For local testing: 'http://10.0.2.2:8000' for Android emulator,
// or your machine's local IP (e.g., 'http://192.168.1.5:8000') for physical devices.
const String API_BASE_URL = 'http://10.0.2.2:8000'; // For Android emulator to host machine

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Quantum Ledger Risk Calculator',
      theme: ThemeData(
        brightness: Brightness.dark,
        primarySwatch: Colors.deepPurple,
        scaffoldBackgroundColor: const Color(0xFF0F0F1A), // Matches your Python app background
        cardColor: const Color(0xFF1A1A2E), // Matches metric card/expander content
        dividerColor: Colors.white12,
        textTheme: GoogleFonts.spaceMonoTextTheme( // Apply Space Mono globally
          Theme.of(context).textTheme,
        ).apply(
          bodyColor: Colors.white, // Default text color
          displayColor: Colors.white,
        ),
        inputDecorationTheme: InputDecorationTheme(
          filled: true,
          fillColor: const Color(0xFF1A1A2E),
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(12.0),
            borderSide: const BorderSide(color: Color(0xFF3A3A50)),
          ),
          enabledBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(12.0),
            borderSide: const BorderSide(color: Color(0xFF3A3A50)),
          ),
          focusedBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(12.0),
            borderSide: const BorderSide(color: Color(0xFFBB86FC), width: 2.0),
          ),
          labelStyle: TextStyle(color: Colors.blue[200]),
          hintStyle: const TextStyle(color: Colors.white54),
        ),
        radioTheme: RadioThemeData(
          fillColor: MaterialStateProperty.all(const Color(0xFFBB86FC)),
        ),
        textButtonTheme: TextButtonThemeData(
          style: TextButton.styleFrom(
            foregroundColor: const Color(0xFFBB86FC), // Purple for buttons
          ),
        ),
        elevatedButtonTheme: ElevatedButtonThemeData(
          style: ElevatedButton.styleFrom(
            backgroundColor: const Color(0xFFBB86FC), // Purple for buttons
            foregroundColor: Colors.white,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(8.0),
            ),
          ),
        ),
        appBarTheme: const AppBarTheme(
          backgroundColor: Color(0xFF1A1A2E),
          foregroundColor: Color(0xFFBB86FC),
          elevation: 0,
        ),
        // Custom styling for headers (simulating your H4 panels)
        cardTheme: CardTheme(
          color: const Color(0xFF151525), // Matches your H4 panel background
          margin: const EdgeInsets.symmetric(vertical: 8.0),
          elevation: 4.0,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12.0),
            side: const BorderSide(color: Color(0xFF28283D), width: 1.0),
          ),
        ),
      ),
      home: const RiskCalculatorScreen(),
    );
  }
}

class RiskCalculatorScreen extends StatefulWidget {
  const RiskCalculatorScreen({super.key});

  @override
  State<RiskCalculatorScreen> createState() => _RiskCalculatorScreenState();
}

class _RiskCalculatorScreenState extends State<RiskCalculatorScreen> {
  // Input Controllers
  final TextEditingController _totalCapitalController = TextEditingController(text: '10000.00');
  final TextEditingController _liquidCapitalController = TextEditingController(text: '10000.00');
  final TextEditingController _riskPercentController = TextEditingController(text: '${DEFAULT_RISK_PERCENT}');
  final TextEditingController _entryPriceController = TextEditingController(text: '100.00');
  final TextEditingController _targetPriceController = TextEditingController(text: '105.00');
  final TextEditingController _leverageController = TextEditingController(text: '${MIN_LEVERAGE}');
  final TextEditingController _stopLossPriceController = TextEditingController(); // Will be set by suggested_stop

  // State Variables
  String _direction = "Long";
  bool _disclaimerAccepted = false;

  // Calculation Results
  double _riskAmount = 0.0;
  double _positionSize = 0.0;
  double _suggestedStop = 0.0;
  double _capitalRequired = 0.0;
  double _expectedReward = 0.0;
  double _rewardToRisk = 0.0;

  // Error/Warning Messages
  String? _errorMessage;
  String? _warningMessage;

  @override
  void initState() {
    super.initState();
    // Initial calculation for suggested stop loss
    _calculateSuggestedStop();
    // Add listeners to update suggested stop loss as inputs change
    _entryPriceController.addListener(_calculateSuggestedStop);
    _liquidCapitalController.addListener(_calculateSuggestedStop);
    _riskPercentController.addListener(_calculateSuggestedStop);
    _leverageController.addListener(_calculateSuggestedStop);
  }

  @override
  void dispose() {
    _totalCapitalController.dispose();
    _liquidCapitalController.dispose();
    _riskPercentController.dispose();
    _entryPriceController.dispose();
    _targetPriceController.dispose();
    _leverageController.dispose();
    _stopLossPriceController.dispose();
    super.dispose();
  }

  Future<void> _calculateSuggestedStop() async {
    final liquidCapital = double.tryParse(_liquidCapitalController.text) ?? 0.0;
    final riskPercent = double.tryParse(_riskPercentController.text) ?? DEFAULT_RISK_PERCENT;
    final entryPrice = double.tryParse(_entryPriceController.text) ?? 0.0;
    final leverage = double.tryParse(_leverageController.text) ?? MIN_LEVERAGE;

    if (entryPrice <= 0 || leverage <= 0 || liquidCapital <= 0) {
      _stopLossPriceController.text = "0.000";
      return;
    }

    try {
      final response = await http.post(
        Uri.parse('$API_BASE_URL/calculate_suggested_stop/'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'entry_price': entryPrice,
          'liquid_capital': liquidCapital,
          'risk_percent': riskPercent,
          'leverage': leverage,
          'direction': _direction,
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        setState(() {
          _suggestedStop = data['suggested_stop'];
          _stopLossPriceController.text = _suggestedStop.toStringAsFixed(3);
        });
      } else {
        final errorData = jsonDecode(response.body);
        print('Error calculating suggested stop: ${errorData['detail']}');
        setState(() {
          _stopLossPriceController.text = "Error";
        });
      }
    } catch (e) {
      print('Network error calculating suggested stop: $e');
      setState(() {
        _stopLossPriceController.text = "Error";
      });
    }
  }

  Future<void> _performFullCalculation() async {
    setState(() {
      _errorMessage = null;
      _warningMessage = null;
    });

    final liquidCapital = double.tryParse(_liquidCapitalController.text) ?? 0.0;
    final riskPercent = double.tryParse(_riskPercentController.text) ?? DEFAULT_RISK_PERCENT;
    final entryPrice = double.tryParse(_entryPriceController.text) ?? 0.0;
    final targetPrice = double.tryParse(_targetPriceController.text) ?? 0.0;
    final leverage = double.tryParse(_leverageController.text) ?? MIN_LEVERAGE;
    final stopLossPrice = double.tryParse(_stopLossPriceController.text) ?? 0.0;


    if (liquidCapital <= 0 || entryPrice <= 0 || leverage <= 0 || stopLossPrice < 0) {
      setState(() {
        _errorMessage = "Please ensure Liquid Capital, Entry Price, Leverage are positive, and Stop Loss Price is non-negative.";
      });
      return;
    }

    // Client-side check for stop loss being too close to entry price
    if ((entryPrice - stopLossPrice).abs() < 0.0001) {
        setState(() {
            _errorMessage = "Stop Loss Price cannot be too close to Entry Price.";
        });
        return;
    }

    // Direction specific validation
    if (_direction == "Long" && stopLossPrice >= entryPrice) {
      setState(() {
        _errorMessage = "For a Long trade, Stop Loss Price must be below Entry Price.";
      });
      return;
    }
    if (_direction == "Short" && stopLossPrice <= entryPrice) {
      setState(() {
        _errorMessage = "For a Short trade, Stop Loss Price must be above Entry Price.";
      });
      return;
    }

    try {
      final response = await http.post(
        Uri.parse('$API_BASE_URL/calculate_trade/'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'liquid_capital': liquidCapital,
          'risk_percent': riskPercent,
          'entry_price': entryPrice,
          'direction': _direction,
          'target_price': targetPrice,
          'leverage': leverage,
          'stop_loss_price': stopLossPrice,
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        setState(() {
          _riskAmount = data['risk_amount'];
          _positionSize = data['position_size'];
          _suggestedStop = data['suggested_stop']; // Update this in case it was refined by API
          _capitalRequired = data['capital_required'];
          _expectedReward = data['expected_reward'];
          _rewardToRisk = data['reward_to_risk'];

          // Check for warnings after successful calculation
          if (_rewardToRisk < MIN_REWARD_RISK_RATIO) {
            _warningMessage = "Reward-to-risk ratio (${_rewardToRisk.toStringAsFixed(2)}:1) is below ${MIN_REWARD_RISK_RATIO}:1. Consider adjusting your target.";
          }
          if (_capitalRequired > liquidCapital) {
            _errorMessage = "Required capital (\$${_capitalRequired.toStringAsFixed(3)}) exceeds your liquid capital (\$${liquidCapital.toStringAsFixed(3)}).";
          } else if (_capitalRequired > 0.8 * liquidCapital) {
            _warningMessage = (_warningMessage ?? "") + "\nTrade uses more than 80% of your liquid capital (\$${_capitalRequired.toStringAsFixed(3)} > 80% of \$${liquidCapital.toStringAsFixed(3)}).";
          }
        });
      } else {
        final errorData = jsonDecode(response.body);
        setState(() {
          _errorMessage = errorData['detail'] ?? "An unknown error occurred.";
        });
      }
    } catch (e) {
      setState(() {
        _errorMessage = "Network error: Could not connect to API. Is the backend running? ($e)";
      });
    }
  }

  Widget _buildInputCard({required String title, required List<Widget> children}) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              title,
              style: const TextStyle(
                color: Color(0xFFBB86FC), // Purple for subheaders
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            ...children,
          ],
        ),
      ),
    );
  }

  Widget _buildMetricCard({required String label, required String value, Color valueColor = const Color(0xFF00FFC0)}) {
    return Card(
      color: const Color(0xFF1A1A2E), // Metric card background
      margin: const EdgeInsets.symmetric(vertical: 4.0),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12.0),
        side: const BorderSide(color: Color(0xFF28283D), width: 1.0),
      ),
      elevation: 6.0, // Increased elevation for shadow
      child: Padding(
        padding: const EdgeInsets.all(12.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              label,
              style: const TextStyle(color: Color(0xFF90CAF9), fontSize: 13), // Label color
            ),
            const SizedBox(height: 4),
            Text(
              value,
              style: GoogleFonts.spaceMono( // Use Space Mono for values
                color: valueColor,
                fontSize: 20,
                fontWeight: FontWeight.bold,
              ),
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('📊 Quantum Ledger', style: TextStyle(color: Color(0xFFBB86FC))),
        centerTitle: true,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // How to Use Expander (Manual recreation of Streamlit expander)
            Card(
              color: const Color(0xFF28283D), // Expander header background
              child: ExpansionTile(
                title: const Text('✨ How to Use This Calculator', style: TextStyle(fontWeight: FontWeight.bold)),
                initiallyExpanded: true,
                collapsedShape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12.0)),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12.0)),
                children: [
                  Container(
                    color: const Color(0xFF1A1A2E), // Expander content background
                    padding: const EdgeInsets.all(16.0),
                    child: const Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('- 💰 Risk exactly **1%** of your **liquid capital** per trade.'),
                        Text('- 📉 Calculate an optimal **stop-loss** to precisely risk 1%.'),
                        Text('- 📈 See your **reward-to-risk** ratio based on your chosen target price.'),
                        Text('- 🔗 Factor in **leverage** to compute the **capital required**.'),
                        Text('- ⚠️ Get **alerts** if your capital or risk rules are violated.'),
                      ],
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 24),

            // Input Sections
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Expanded(
                  child: _buildInputCard(
                    title: '🏦 Capital Settings',
                    children: [
                      _buildTextField(_totalCapitalController, '💼 Total Capital (\$)', keyboardType: TextInputType.number),
                      _buildTextField(_liquidCapitalController, '💧 Liquid Capital for Trading (\$)', keyboardType: TextInputType.number),
                      _buildTextField(_riskPercentController, '⚠️ Risk % per trade', keyboardType: TextInputType.number),
                      _buildTextField(_leverageController, '🧬 Leverage (e.g. 1 = no leverage)', keyboardType: TextInputType.number),
                    ],
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: _buildInputCard(
                    title: '📊 Trade Settings',
                    children: [
                      _buildTextField(_entryPriceController, '🎯 Entry Price (\$)', keyboardType: TextInputType.number),
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text('📈 Are you going Long or Short?', style: TextStyle(color: Colors.white70)),
                          Row(
                            children: [
                              ChoiceChip(
                                label: const Text('Long'),
                                selected: _direction == 'Long',
                                onSelected: (selected) {
                                  if (selected) {
                                    setState(() {
                                      _direction = 'Long';
                                    });
                                    _calculateSuggestedStop();
                                  }
                                },
                                selectedColor: const Color(0xFF00FF80), // Green for Long
                                backgroundColor: const Color(0xFF28283D),
                                labelStyle: TextStyle(color: _direction == 'Long' ? Colors.black : Colors.white),
                              ),
                              const SizedBox(width: 8),
                              ChoiceChip(
                                label: const Text('Short'),
                                selected: _direction == 'Short',
                                onSelected: (selected) {
                                  if (selected) {
                                    setState(() {
                                      _direction = 'Short';
                                    });
                                    _calculateSuggestedStop();
                                  }
                                },
                                selectedColor: const Color(0xFFFF6347), // Red for Short
                                backgroundColor: const Color(0xFF28283D),
                                labelStyle: TextStyle(color: _direction == 'Short' ? Colors.black : Colors.white),
                              ),
                            ],
                          ),
                        ],
                      ),
                      _buildTextField(_targetPriceController, '🎯 Target Price (\$)', keyboardType: TextInputType.number),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 24),

            // Stop Loss Input (separate card)
            _buildInputCard(
              title: '🛑 Stop Loss Adjustment',
              children: [
                _buildTextField(
                  _stopLossPriceController,
                  '🛑 Stop Loss Price (\$)',
                  keyboardType: TextInputType.number,
                  helperText: 'Pre-filled with suggested stop-loss; override as needed.',
                ),
              ],
            ),
            const SizedBox(height: 24),

            // Calculate Button
            ElevatedButton(
              onPressed: _disclaimerAccepted ? _performFullCalculation : null,
              style: ElevatedButton.styleFrom(
                padding: const EdgeInsets.symmetric(vertical: 16),
                backgroundColor: const Color(0xFFBB86FC), // Purple button
                foregroundColor: Colors.white,
                textStyle: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10.0)),
                elevation: 8,
                shadowColor: const Color(0xFFBB86FC).withOpacity(0.5),
              ),
              child: const Text('Calculate Trade'),
            ),
            const SizedBox(height: 24),

            // Error/Warning Messages
            if (_errorMessage != null)
              Container(
                padding: const EdgeInsets.all(16),
                margin: const EdgeInsets.only(bottom: 16),
                decoration: BoxDecoration(
                  color: const Color(0xFF260000), // Error background
                  border: const Border(left: BorderSide(color: Color(0xFFFF4747), width: 6)), // Red border
                  borderRadius: BorderRadius.circular(10),
                  boxShadow: [BoxShadow(color: const Color(0xFFFF4747).withOpacity(0.4), blurRadius: 8)],
                ),
                child: Text(
                  '🚫 Error: $_errorMessage',
                  style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
                ),
              ),
            if (_warningMessage != null && _errorMessage == null) // Only show warning if no error
              Container(
                padding: const EdgeInsets.all(16),
                margin: const EdgeInsets.only(bottom: 16),
                decoration: BoxDecoration(
                  color: const Color(0xFF262100), // Warning background
                  border: const Border(left: BorderSide(color: Color(0xFFFFD700), width: 6)), // Gold border
                  borderRadius: BorderRadius.circular(10),
                  boxShadow: [BoxShadow(color: const Color(0xFFFFD700).withOpacity(0.4), blurRadius: 8)],
                ),
                child: Text(
                  '⚠️ Warning: $_warningMessage',
                  style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
                ),
              ),
            const SizedBox(height: 24),

            // Trade Summary
            const Text(
              '📈 Trade Summary',
              style: TextStyle(
                color: Color(0xFF90CAF9),
                fontSize: 22,
                fontWeight: FontWeight.bold,
              ),
            ),
            const Divider(color: Colors.white12, thickness: 1, height: 20),
            Row(
              children: [
                Expanded(
                  child: Column(
                    children: [
                      _buildMetricCard(label: '💰 Max Risk Allowed', value: '\$${_riskAmount.toStringAsFixed(3)}'),
                      _buildMetricCard(label: '📦 Position Size', value: '${_positionSize.toStringAsFixed(3)} units'),
                      _buildMetricCard(label: '🛑 Suggested Stop Loss', value: '\$${_suggestedStop.toStringAsFixed(3)}'),
                    ],
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    children: [
                      _buildMetricCard(label: '💸 Capital Required', value: '\$${_capitalRequired.toStringAsFixed(3)}'),
                      _buildMetricCard(label: '🎯 Expected Reward', value: '\$${_expectedReward.toStringAsFixed(3)}'),
                      _buildMetricCard(label: '⚖️ Reward-to-Risk Ratio', value: '${_rewardToRisk.toStringAsFixed(2)}:1'),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 24),

            // Disclaimer
            const Text(
              '📢 Disclaimer',
              style: TextStyle(
                color: Color(0xFF90CAF9),
                fontSize: 22,
                fontWeight: FontWeight.bold,
              ),
            ),
            const Divider(color: Colors.white12, thickness: 1, height: 20),
            const Text(
              'This tool is provided for educational purposes only and does not constitute financial advice.\n\nTrading involves risk. Always consult a licensed financial advisor and only use capital you can afford to lose.',
              style: TextStyle(fontSize: 14),
            ),
            Row(
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                Checkbox(
                  value: _disclaimerAccepted,
                  onChanged: (bool? newValue) {
                    setState(() {
                      _disclaimerAccepted = newValue ?? false;
                    });
                  },
                  activeColor: const Color(0xFF00FFC0), // Green for checkbox
                  checkColor: Colors.black,
                ),
                const Text('✅ I understand and accept the disclaimer'),
              ],
            ),
            if (!_disclaimerAccepted)
              Container(
                padding: const EdgeInsets.all(12),
                margin: const EdgeInsets.only(top: 8),
                decoration: BoxDecoration(
                  color: Colors.blueGrey.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: const Text(
                  'Please acknowledge the disclaimer to proceed.',
                  style: TextStyle(color: Colors.blueGrey, fontStyle: FontStyle.italic),
                ),
              ),
            const SizedBox(height: 24),

            // Footer
            const Divider(color: Colors.white12, thickness: 1, height: 20),
            const Text(
              '© 2025 Quantum Ledger. All rights reserved.',
              textAlign: TextAlign.center,
              style: TextStyle(color: Color(0xFF7F8C8D), fontSize: 11),
            ),
          ],
        ),
      ),
    );
  }

  // Helper for text fields to apply consistent styling
  Widget _buildTextField(TextEditingController controller, String label, {TextInputType keyboardType = TextInputType.text, String? helperText}) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8.0),
      child: TextField(
        controller: controller,
        keyboardType: keyboardType,
        decoration: InputDecoration(
          labelText: label,
          helperText: helperText,
          helperStyle: const TextStyle(fontSize: 11, color: Colors.white60),
        ),
        style: GoogleFonts.spaceMono(color: const Color(0xFF00FFC0)), // Neon green text
      ),
    );
  }
}
