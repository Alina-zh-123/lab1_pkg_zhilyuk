import javafx.application.Application;
import javafx.beans.value.ChangeListener;
import javafx.geometry.Insets;
import javafx.scene.Scene;
import javafx.scene.control.*;
import javafx.scene.layout.GridPane;
import javafx.scene.layout.HBox;
import javafx.scene.layout.VBox;
import javafx.scene.paint.Color;
import javafx.scene.shape.Rectangle;
import javafx.stage.Stage;

public class Main extends Application {
    
    private Color currentColor = Color.WHITE;
    private boolean updating = false;
    
    private Slider sliderR, sliderG, sliderB;
    private TextField textR, textG, textB;
    
    private Slider sliderX, sliderY_xyz, sliderZ;
    private TextField textX, textY_xyz, textZ;
    
    private Slider sliderC, sliderM, sliderY_cmyk, sliderK;
    private TextField textC, textM, textY_cmyk, textK;
    
    private Label warningLabel;
    private Rectangle colorPreview;

    @Override
    public void start(Stage primaryStage) {
        primaryStage.setTitle("Конструктор цвета - RGB, XYZ, CMYK");
        
        VBox mainContainer = new VBox(20);
        mainContainer.setPadding(new Insets(20));
        mainContainer.setStyle("-fx-background-color: #232b43;");
        
        colorPreview = new Rectangle(830, 80);
        colorPreview.setArcWidth(20);
        colorPreview.setArcHeight(20);
        colorPreview.setFill(currentColor);
        
        warningLabel = new Label();
        warningLabel.setStyle("-fx-text-fill: #ff6b6b; -fx-font-weight: bold;");
        
        VBox rgbPanel = createRGBPanel();
        VBox xyzPanel = createXYZPanel();
        VBox cmykPanel = createCMYKPanel();
        
        ColorPicker colorPicker = new ColorPicker(currentColor);
        colorPicker.setOnAction(e -> {
            if (!updating) {
                setColor(colorPicker.getValue());
            }
        });
        
        HBox colorModelsPanel = new HBox(20);
        colorModelsPanel.getChildren().addAll(rgbPanel, xyzPanel, cmykPanel);
        
        HBox topPanel = new HBox(20, colorPreview, colorPicker);
        
        mainContainer.getChildren().addAll(
            topPanel, warningLabel, colorModelsPanel
        );
        
        Scene scene = new Scene(mainContainer, 1100, 440);
        primaryStage.setScene(scene);
        primaryStage.show();
        
        updateAllDisplays();
    }
    
    private VBox createRGBPanel() {
        Label title = new Label("RGB Color Model");
        title.setStyle("-fx-font-size: 18px; -fx-text-fill: white; -fx-font-weight: bold;");
        
        sliderR = createColorSlider(0, 255, 255);
        sliderG = createColorSlider(0, 255, 255);
        sliderB = createColorSlider(0, 255, 255);
        
        textR = createColorTextField("255");
        textG = createColorTextField("255");
        textB = createColorTextField("255");
        
        bindRGBControls();
        
        GridPane rgbGrid = new GridPane();
        rgbGrid.setHgap(10);
        rgbGrid.setVgap(8);
        rgbGrid.add(new Label("R:"), 0, 0);
        rgbGrid.add(sliderR, 1, 0);
        rgbGrid.add(textR, 2, 0);
        rgbGrid.add(new Label("G:"), 0, 1);
        rgbGrid.add(sliderG, 1, 1);
        rgbGrid.add(textG, 2, 1);
        rgbGrid.add(new Label("B:"), 0, 2);
        rgbGrid.add(sliderB, 1, 2);
        rgbGrid.add(textB, 2, 2);
        
        VBox panel = new VBox(15, title, rgbGrid);
        panel.setStyle("-fx-background-color: #3b4359; -fx-padding: 15; -fx-background-radius: 10;");
        panel.setPrefWidth(350);
        return panel;
    }
    
    private VBox createXYZPanel() {
        Label title = new Label("XYZ Color Model");
        title.setStyle("-fx-font-size: 18px; -fx-text-fill: white; -fx-font-weight: bold;");
        
        sliderX = createColorSlider(0, 95, 95);
        sliderY_xyz = createColorSlider(0, 100, 100);
        sliderZ = createColorSlider(0, 109, 109);
        
        textX = createColorTextField("95.0");
        textY_xyz = createColorTextField("100.0");
        textZ = createColorTextField("109.0");
        
        bindXYZControls();
        
        GridPane xyzGrid = new GridPane();
        xyzGrid.setHgap(10);
        xyzGrid.setVgap(8);
        xyzGrid.add(new Label("X:"), 0, 0);
        xyzGrid.add(sliderX, 1, 0);
        xyzGrid.add(textX, 2, 0);
        xyzGrid.add(new Label("Y:"), 0, 1);
        xyzGrid.add(sliderY_xyz, 1, 1);
        xyzGrid.add(textY_xyz, 2, 1);
        xyzGrid.add(new Label("Z:"), 0, 2);
        xyzGrid.add(sliderZ, 1, 2);
        xyzGrid.add(textZ, 2, 2);
        
        VBox panel = new VBox(15, title, xyzGrid);
        panel.setStyle("-fx-background-color: #3b4359; -fx-padding: 15; -fx-background-radius: 10;");
        panel.setPrefWidth(350);
        return panel;
    }
    
    private VBox createCMYKPanel() {
        Label title = new Label("CMYK Color Model");
        title.setStyle("-fx-font-size: 18px; -fx-text-fill: white; -fx-font-weight: bold;");
        
        sliderC = createColorSlider(0, 100, 0);
        sliderM = createColorSlider(0, 100, 0);
        sliderY_cmyk = createColorSlider(0, 100, 0);
        sliderK = createColorSlider(0, 100, 0);
        
        textC = createColorTextField("0");
        textM = createColorTextField("0");
        textY_cmyk = createColorTextField("0");
        textK = createColorTextField("0");
        
        bindCMYKControls();
        
        GridPane cmykGrid = new GridPane();
        cmykGrid.setHgap(10);
        cmykGrid.setVgap(8);
        cmykGrid.add(new Label("C:"), 0, 0);
        cmykGrid.add(sliderC, 1, 0);
        cmykGrid.add(textC, 2, 0);
        cmykGrid.add(new Label("M:"), 0, 1);
        cmykGrid.add(sliderM, 1, 1);
        cmykGrid.add(textM, 2, 1);
        cmykGrid.add(new Label("Y:"), 0, 2);
        cmykGrid.add(sliderY_cmyk, 1, 2);
        cmykGrid.add(textY_cmyk, 2, 2);
        cmykGrid.add(new Label("K:"), 0, 3);
        cmykGrid.add(sliderK, 1, 3);
        cmykGrid.add(textK, 2, 3);
        
        VBox panel = new VBox(15, title, cmykGrid);
        panel.setStyle("-fx-background-color: #3b4359; -fx-padding: 15; -fx-background-radius: 10;");
        panel.setPrefWidth(350);
        return panel;
    }
    
    private Slider createColorSlider(double min, double max, double value) {
        Slider slider = new Slider(min, max, value);
        slider.setShowTickLabels(true);
        slider.setShowTickMarks(true);
        slider.setMajorTickUnit((max - min) / 4);
        slider.setBlockIncrement(1);
        slider.setPrefWidth(200);
        return slider;
    }
    
    private TextField createColorTextField(String initialValue) {
        TextField field = new TextField(initialValue);
        field.setPrefWidth(60);
        return field;
    }
    
    private void bindRGBControls() {
        ChangeListener<Number> rgbSliderListener = (obs, oldVal, newVal) -> {
            if (!updating) {
                int r = (int) sliderR.getValue();
                int g = (int) sliderG.getValue();
                int b = (int) sliderB.getValue();
                setColor(Color.rgb(r, g, b));
            }
        };
        
        sliderR.valueProperty().addListener(rgbSliderListener);
        sliderG.valueProperty().addListener(rgbSliderListener);
        sliderB.valueProperty().addListener(rgbSliderListener);
        
        textR.textProperty().addListener((obs, oldVal, newVal) -> updateFromRGBText());
        textG.textProperty().addListener((obs, oldVal, newVal) -> updateFromRGBText());
        textB.textProperty().addListener((obs, oldVal, newVal) -> updateFromRGBText());
    }
    
    private void bindXYZControls() {
        ChangeListener<Number> xyzSliderListener = (obs, oldVal, newVal) -> {
            if (!updating) {
                double x = sliderX.getValue() / 100.0;
                double y = sliderY_xyz.getValue() / 100.0;
                double z = sliderZ.getValue() / 100.0;
                Color xyzColor = xyzToRgb(x, y, z);
                setColor(xyzColor);
            }
        };
        
        sliderX.valueProperty().addListener(xyzSliderListener);
        sliderY_xyz.valueProperty().addListener(xyzSliderListener);
        sliderZ.valueProperty().addListener(xyzSliderListener);
        
        textX.textProperty().addListener((obs, oldVal, newVal) -> updateFromXYZText());
        textY_xyz.textProperty().addListener((obs, oldVal, newVal) -> updateFromXYZText());
        textZ.textProperty().addListener((obs, oldVal, newVal) -> updateFromXYZText());
    }
    
    private void bindCMYKControls() {
        ChangeListener<Number> cmykSliderListener = (obs, oldVal, newVal) -> {
            if (!updating) {
                double c = sliderC.getValue() / 100.0;
                double m = sliderM.getValue() / 100.0;
                double y = sliderY_cmyk.getValue() / 100.0;
                double k = sliderK.getValue() / 100.0;
                Color cmykColor = cmykToRgb(c, m, y, k);
                setColor(cmykColor);
            }
        };
        
        sliderC.valueProperty().addListener(cmykSliderListener);
        sliderM.valueProperty().addListener(cmykSliderListener);
        sliderY_cmyk.valueProperty().addListener(cmykSliderListener);
        sliderK.valueProperty().addListener(cmykSliderListener);
        
        textC.textProperty().addListener((obs, oldVal, newVal) -> updateFromCMYKText());
        textM.textProperty().addListener((obs, oldVal, newVal) -> updateFromCMYKText());
        textY_cmyk.textProperty().addListener((obs, oldVal, newVal) -> updateFromCMYKText());
        textK.textProperty().addListener((obs, oldVal, newVal) -> updateFromCMYKText());
    }
    
    private void updateFromRGBText() {
        if (!updating) {
            try {
                int r = Integer.parseInt(textR.getText());
                int g = Integer.parseInt(textG.getText());
                int b = Integer.parseInt(textB.getText());
                
                if (r >= 0 && r <= 255 && g >= 0 && g <= 255 && b >= 0 && b <= 255) {
                    setColor(Color.rgb(r, g, b));
                    warningLabel.setText("");
                } else {
                    warningLabel.setText("Некорректный формат RGB значений");
                }
            } catch (NumberFormatException e) {
                warningLabel.setText("Некорректный формат RGB значений");
            }
        }
    }
    
    private void updateFromXYZText() {
        if (!updating) {
            try {
                double x = Double.parseDouble(textX.getText());
                double y = Double.parseDouble(textY_xyz.getText());
                double z = Double.parseDouble(textZ.getText());
                
                Color xyzColor = xyzToRgb(x/100.0, y/100.0, z/100.0);
                setColor(xyzColor);
                
            } catch (NumberFormatException e) {
                warningLabel.setText("Некорректный формат XYZ значений");
            }
        }
    }
    
    private void updateFromCMYKText() {
        if (!updating) {
            try {
                double c = Double.parseDouble(textC.getText()) / 100.0;
                double m = Double.parseDouble(textM.getText()) / 100.0;
                double y = Double.parseDouble(textY_cmyk.getText()) / 100.0;
                double k = Double.parseDouble(textK.getText()) / 100.0;
                
                if (c >= 0 && c <= 1 && m >= 0 && m <= 1 && y >= 0 && y <= 1 && k >= 0 && k <= 1) {
                    Color cmykColor = cmykToRgb(c, m, y, k);
                    setColor(cmykColor);
                    warningLabel.setText("");
                } else {
                    warningLabel.setText("Некорректный формат CMYK значений");
                }
            } catch (NumberFormatException e) {
                warningLabel.setText("Некорректный формат CMYK значений");
            }
        }
    }
    
    private void setColor(Color newColor) {
        updating = true;
        currentColor = newColor;
        updateAllDisplays();
        updating = false;
    }
    
    private void updateAllDisplays() {
        updateRGBDisplay();
        updateXYZDisplay();
        updateCMYKDisplay();
        colorPreview.setFill(currentColor);
    }
    
    private void updateRGBDisplay() {
        int r = (int) (currentColor.getRed() * 255);
        int g = (int) (currentColor.getGreen() * 255);
        int b = (int) (currentColor.getBlue() * 255);
        
        sliderR.setValue(r);
        sliderG.setValue(g);
        sliderB.setValue(b);
        
        textR.setText(String.valueOf(r));
        textG.setText(String.valueOf(g));
        textB.setText(String.valueOf(b));
    }
    
    private void updateXYZDisplay() {
        double[] xyz = rgbToXyz(currentColor);
        sliderX.setValue(xyz[0] * 100);
        sliderY_xyz.setValue(xyz[1] * 100);
        sliderZ.setValue(xyz[2] * 100);
        
        textX.setText(String.format("%.2f", xyz[0] * 100));
        textY_xyz.setText(String.format("%.2f", xyz[1] * 100));
        textZ.setText(String.format("%.2f", xyz[2] * 100));
    }
    
    private void updateCMYKDisplay() {
        double[] cmyk = rgbToCmyk(currentColor);
        sliderC.setValue(cmyk[0] * 100);
        sliderM.setValue(cmyk[1] * 100);
        sliderY_cmyk.setValue(cmyk[2] * 100);
        sliderK.setValue(cmyk[3] * 100);
        
        textC.setText(String.format("%.1f", cmyk[0] * 100));
        textM.setText(String.format("%.1f", cmyk[1] * 100));
        textY_cmyk.setText(String.format("%.1f", cmyk[2] * 100));
        textK.setText(String.format("%.1f", cmyk[3] * 100));
    }
    
    private double[] rgbToXyz(Color color) {
        double r = color.getRed();
        double g = color.getGreen();
        double b = color.getBlue();
        
        double x = 0.4124564 * r + 0.3575761 * g + 0.1804375 * b;
        double y = 0.2126729 * r + 0.7151522 * g + 0.0721750 * b;
        double z = 0.0193339 * r + 0.1191920 * g + 0.9503041 * b;
        
        return new double[]{x, y, z};
    }
    
    private Color xyzToRgb(double x, double y, double z) {
        double r = 3.2404542 * x - 1.5371385 * y - 0.4985314 * z;
        double g = -0.9692660 * x + 1.8760108 * y + 0.0415560 * z;
        double b = 0.0556434 * x - 0.2040259 * y + 1.0572252 * z;
        
        boolean clipped = false;
        r = clamp(r, 0, 1);
        g = clamp(g, 0, 1);
        b = clamp(b, 0, 1);
        
        if (r != Math.max(0, Math.min(1, r)) || 
            g != Math.max(0, Math.min(1, g)) || 
            b != Math.max(0, Math.min(1, b))) {
            clipped = true;
        }
        
        if (clipped) {
            warningLabel.setText("Внимание: XYZ значения выходят за границы RGB. Произведено обрезание.");
        } else {
            warningLabel.setText("");
        }
        
        return Color.color(r, g, b);
    }
    
    private double[] rgbToCmyk(Color color) {
        double r = color.getRed();
        double g = color.getGreen();
        double b = color.getBlue();
        
        double k = 1 - Math.max(r, Math.max(g, b));
        double c = (1 - r - k) / (1 - k);
        double m = (1 - g - k) / (1 - k);
        double y = (1 - b - k) / (1 - k);
        
        if (Double.isNaN(c)) c = 0;
        if (Double.isNaN(m)) m = 0;
        if (Double.isNaN(y)) y = 0;
        
        return new double[]{c, m, y, k};
    }
    
    private Color cmykToRgb(double c, double m, double y, double k) {
        double r = (1 - c) * (1 - k);
        double g = (1 - m) * (1 - k);
        double b = (1 - y) * (1 - k);
        
        return Color.color(r, g, b);
    }
    
    private double clamp(double value, double min, double max) {
        return Math.max(min, Math.min(max, value));
    }
    
    public static void main(String[] args) {
        launch(args);
    }
}